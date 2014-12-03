import itertools
import logging
import os
import re
import subprocess
import time

_log = logging.getLogger(__name__)

"""
Minimally wraps CoreSimulator functionality through simctl.

If possible, use real CoreSimulator.framework functionality by linking to the framework itself.
Do not use PyObjC to dlopen the framework.
"""


class DeviceType(object):
    """
    Represents a CoreSimulator device type.
    """
    def __init__(self, name, identifier):
        """
        :param name: The device type's human-readable name
        :type name: str
        :param identifier: The CoreSimulator identifier.
        :type identifier: str
        """
        self.name = name
        self.identifier = identifier

    @classmethod
    def from_name(cls, name):
        """
        :param name: The name for the desired device type.
        :type name: str
        :returns: A `DeviceType` object with the specified identifier or throws a TypeError if it doesn't exist.
        :rtype: DeviceType
        """
        identifier = None
        for device_type in Simulator().device_types:
            if device_type.name == name:
                identifier = device_type.identifier
                break

        if identifier is None:
            raise TypeError('A device type with name "{name}" does not exist.'.format(name=name))

        return DeviceType(name, identifier)

    @classmethod
    def from_identifier(cls, identifier):
        """
        :param identifier: The CoreSimulator identifier for the desired runtime.
        :type identifier: str
        :returns: A `Runtime` object witht the specified identifier or throws a TypeError if it doesn't exist.
        :rtype: DeviceType
        """
        name = None
        for device_type in Simulator().device_types:
            if device_type.identifier == identifier:
                name = device_type.name
                break

        if name is None:
            raise TypeError('A device type with identifier "{identifier}" does not exist.'.format(
                identifier=identifier))

        return DeviceType(name, identifier)

    def __eq__(self, other):
        return (self.name == other.name) and (self.identifier == other.identifier)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<DeviceType "{name}": {identifier}>'.format(name=self.name, identifier=self.identifier)


class Runtime(object):
    """
    Represents a CoreSimulator runtime associated with an iOS SDK.
    """

    def __init__(self, version, identifier, available, devices=None):
        """
        :param version: The iOS SDK version
        :type version: tuple
        :param identifier: The CoreSimualtor runtime identifier
        :type identifier: str
        :param availability: Whether the runtime is available for use.
        :type availability: bool
        :param devices: A list of devices under this runtime
        :type devices: list or None
        """
        self.version = version
        self.identifier = identifier
        self.available = available
        self.devices = devices or []

    @classmethod
    def from_identifier(cls, identifier):
        """
        :param identifier: The identifier for the desired CoreSimulator runtime.
        :type identifier: str
        :returns: A `Runtime` object with the specified identifier or throws a TypeError if it doesn't exist.
        :rtype: Runtime
        """
        runtime = None
        for runtime in Simulator().runtimes:
            if runtime.identifier == identifier:
                break
        if runtime is None:
            raise TypeError('A runtime with identifier "{identifier}" does not exist.'.format(identifier=identifier))
        return runtime

    def __eq__(self, other):
        return (self.version == other.version) and (self.identifier == other.identifier)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Runtime {version}: {identifier}. Available: {available}, {num_devices} devices>'.format(
            version='.'.join(map(str, self.version)),
            identifier=self.identifier,
            available=self.available,
            num_devices=len(self.devices))


class Device(object):
    """
    Represents a CoreSimulator device underneath a runtime
    """

    def __init__(self, name, udid, state, available, runtime):
        """
        :param name: The device name
        :type name: str
        :param udid: The device UDID (a UUID string)
        :type udid: str
        :param state: The last known device state
        :type state: str
        :param available: Whether the device is available for use.
        :type available: bool
        :param runtime: The iOS Simulator runtime that hosts this device
        :type runtime: Runtime
        """
        self.name = name
        self.udid = udid
        self.state = state
        self.available = available
        self.runtime = runtime

    @property
    def path(self):
        """
        :returns: The filesystem path that contains the simulator device's data.
        :rtype: str
        """
        return os.path.realpath(
            os.path.expanduser(
                os.path.join('~/Library/Developer/CoreSimulator/Devices', self.udid)))

    @classmethod
    def create(cls, name, device_type, runtime):
        """
        Create a new CoreSimulator device.
        :param name: The name of the device.
        :type name: str
        :param device_type: The CoreSimulatort device type.
        :type device_type: DeviceType
        :param runtime:  The CoreSimualtor runtime.
        :type runtime: Runtime
        :return: The new device or raises a CalledProcessError if ``simctl create`` failed.
        :rtype: Device
        """
        sim = Simulator()
        subprocess.check_call(['xcrun', 'simctl', 'create', name, device_type.identifier, runtime.identifier])

        device = None
        while device is None:
            sim.refresh()
            device = sim.device(name, runtime)
            if device is None or device.state == 'Creating':
                time.sleep(2)
            else:
                break
        return device

    def __eq__(self, other):
        return self.udid == other.udid

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Device "{name}": {udid}. State: {state}. Runtime: {runtime}, Available: {available}>'.format(
            name=self.name,
            udid=self.udid,
            state=self.state,
            available=self.available,
            runtime=self.runtime.identifier)


class Simulator(object):
    """
    Represents the iOS Simulator infrastructure under the currently select Xcode.app bundle.
    """
    device_type_re = re.compile('(?P<name>[^(]+)\((?P<identifier>[^)]+)\)')
    runtime_re = re.compile(
        'iOS (?P<version>[0-9]+\.[0-9]) \([0-9]+\.[0-9]+ - (?P<build_version>[^)]+)\) \((?P<identifier>[^)]+)\)( \((?P<availability>[^)]+)\))?')
    version_re = re.compile('-- iOS (?P<version>[0-9]+\.[0-9]+) --')
    devices_re = re.compile(
        '\s*(?P<name>[^(]+ )\((?P<udid>[^)]+)\) \((?P<state>[^)]+)\)( \((?P<availability>[^)]+)\))?')

    def __init__(self):
        self.runtimes = []
        self.device_types = []
        self.refresh()

    def refresh(self):
        """
        Refresh runtime and device type information from ``simctl list``.
        """
        command = ['xcrun', 'simctl', 'list']
        simctl_p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = simctl_p.communicate()
        if simctl_p.returncode != 0:
            raise RuntimeError(
                '{command} failed:\n{stdout}\n{stderr}'.format(command=' '.join(command), stdout=stdout, stderr=stderr))

        lines = (line for line in stdout.splitlines())
        device_types_header = next(lines)
        if device_types_header != '== Device Types ==':
            raise RuntimeError('Expected == Device Types == header but got: "{}"'.format(device_types_header))
        self._parse_device_types(lines)

    def _parse_device_types(self, lines):
        """
        Parse device types from ``simctl list``.
        :param lines: A generator for the output lines from ``simctl list``.
        :type lines: genexpr
        :return: None
        """
        for line in lines:
            device_type_match = self.device_type_re.match(line)
            if not device_type_match:
                if line != '== Runtimes ==':
                    raise RuntimeError('Expected == Runtimes == header but got: "{}"'.format(line))
                break
            device_type = DeviceType(name=device_type_match.group('name').rstrip(),
                                     identifier=device_type_match.group('identifier'))
            self.device_types.append(device_type)

        self._parse_runtimes(lines)

    def _parse_runtimes(self, lines):
        """
        Continue to parse runtimes from ``simctl list``.
        :param lines: A generator for the output lines from ``simctl list``.
        :type lines: genexpr
        :return: None
        """
        for line in lines:
            runtime_match = self.runtime_re.match(line)
            if not runtime_match:
                if line != '== Devices ==':
                    raise RuntimeError('Expected == Devices == header but got: "{}"'.format(line))
                break
            version = tuple(map(int, runtime_match.group('version').split('.')))
            runtime = Runtime(version=version,
                              identifier=runtime_match.group('identifier'),
                              available=runtime_match.group('availability') is None)
            self.runtimes.append(runtime)
        self._parse_devices(lines)

    def _parse_devices(self, lines):
        """
        Continue to parse devices from ``simctl list``.
        :param lines: A generator for the output lines from ``simctl list``.
        :type lines: genexpr
        :return: None
        """
        current_runtime = None
        for line in lines:
            version_match = self.version_re.match(line)
            if version_match:
                version = tuple(map(int, version_match.group('version').split('.')))
                current_runtime = self.runtime(version=version)
                assert current_runtime
                continue
            device_match = self.devices_re.match(line)
            if not device_match:
                raise RuntimeError('Expected an iOS Simulator device line, got "{}"'.format(line))
            device = Device(name=device_match.group('name').rstrip(),
                            udid=device_match.group('udid'),
                            state=device_match.group('state'),
                            available=device_match.group('availability') is None,
                            runtime=current_runtime)
            current_runtime.devices.append(device)

    def device_type(self, name=None, identifier=None):
        """
        :param name: The short name of the device type.
        :type name: str
        :param identifier: The CoreSimulator identifier of the desired device type.
        :type identifier: str
        :return: A device type with the specified name and/or identifier, or None if one doesn't exist as such.
        :rtype: DeviceType
        """
        for device_type in self.device_types:
            if name and device_type.name != name:
                continue
            if identifier and device_type.identifier != identifier:
                continue
            return device_type
        return None

    def runtime(self, version=None, identifier=None):
        """
        :param version: The iOS version of the desired runtime.
        :type version: tuple
        :param identifier: The CoreSimulator identifier of the desired runtime.
        :type identifier: str
        :return: A runtime with the specified version and/or identifier, or None if one doesn't exist as such.
        :rtype: Runtime or None
        """
        if version is None and identifier is None:
            raise TypeError('Must supply version and/or identifier.')

        for runtime in self.runtimes:
            if version and runtime.version != version:
                continue
            if identifier and runtime.identifier != identifier:
                continue
            return runtime
        return None

    def device(self, name=None, runtime=None):
        """
        :param name: The name of the desired device.
        :type name: str
        :param runtime: The runtime of the desired device.
        :type runtime: Runtime
        :return: A device with the specified name and/or runtime, or None if one doesn't exist as such
        :rtype: Device or None
        """
        if name is None and runtime is None:
            raise TypeError('Must supply name and/or runtime.')

        for device in self.devices:
            if name and device.name != name:
                continue
            if runtime and device.runtime != runtime:
                continue
            return device
        return None

    @property
    def devices(self):
        """
        :return: An iterator of all devices from all runtimes.
        :rtype: iter
        """
        return itertools.chain(*[runtime.devices for runtime in self.runtimes])

    @property
    def latest_runtime(self):
        """
        :return: Returns a Runtime object with the highest version.
        :rtype: Runtime or None
        """
        if not self.runtimes:
            return None
        return sorted(self.runtimes, key=lambda runtime: runtime.version)[-1]

    def testing_device(self, device_type, runtime):
        """
        Get an iOS Simulator device for testing.
        :param device_type: The CoreSimulator device type.
        :type device_type: DeviceType
        :param runtime: The CoreSimulator runtime.
        :type runtime: Runtime
        :return: A dictionary describing the device.
        :rtype: Device
        """
        # Check to see if the testing device already exists
        name = device_type.name + ' WebKit Tester'
        return self.device(name=name, runtime=runtime) or Device.create(name, device_type, runtime)

    def __repr__(self):
        return '<iOS Simulator: {num_runtimes} runtimes, {num_device_types} device types>'.format(
            num_runtimes=len(self.runtimes),
            num_device_types=len(self.device_types))

    def __str__(self):
        description = ['iOS Simulator:']
        description += map(str, self.runtimes)
        description += map(str, self.device_types)
        description += map(str, self.devices)
        return '\n'.join(description)
