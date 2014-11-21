/*
    This file is part of the WebKit open source project.
    This file has been generated by generate-bindings.pl. DO NOT MODIFY!

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Library General Public
    License as published by the Free Software Foundation; either
    version 2 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Library General Public License for more details.

    You should have received a copy of the GNU Library General Public License
    along with this library; see the file COPYING.LIB.  If not, write to
    the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
    Boston, MA 02110-1301, USA.
*/

#include "config.h"

#if ENABLE(SQL_DATABASE)

#include "JSTestCallback.h"

#include "JSDOMStringList.h"
#include "JSTestNode.h"
#include "ScriptExecutionContext.h"
#include "SerializedScriptValue.h"
#include <runtime/JSLock.h>

using namespace JSC;

namespace WebCore {

JSTestCallback::JSTestCallback(JSObject* callback, JSDOMGlobalObject* globalObject)
    : TestCallback()
    , ActiveDOMCallback(globalObject->scriptExecutionContext())
    , m_data(new JSCallbackData(callback, globalObject))
{
}

JSTestCallback::~JSTestCallback()
{
    ScriptExecutionContext* context = scriptExecutionContext();
    // When the context is destroyed, all tasks with a reference to a callback
    // should be deleted. So if the context is 0, we are on the context thread.
    if (!context || context->isContextThread())
        delete m_data;
    else
        context->postTask(DeleteCallbackDataTask(m_data));
#ifndef NDEBUG
    m_data = 0;
#endif
}


// Functions

bool JSTestCallback::callbackWithNoParam()
{
    if (!canInvokeCallback())
        return true;

    Ref<JSTestCallback> protect(*this);

    JSLockHolder lock(m_data->globalObject()->vm());

    MarkedArgumentBuffer args;

    bool raisedException = false;
    m_data->invokeCallback(args, &raisedException);
    return !raisedException;
}

bool JSTestCallback::callbackWithArrayParam(RefPtr<Float32Array> arrayParam)
{
    if (!canInvokeCallback())
        return true;

    Ref<JSTestCallback> protect(*this);

    JSLockHolder lock(m_data->globalObject()->vm());

    ExecState* exec = m_data->globalObject()->globalExec();
    MarkedArgumentBuffer args;
    args.append(toJS(exec, m_data->globalObject(), arrayParam));

    bool raisedException = false;
    m_data->invokeCallback(args, &raisedException);
    return !raisedException;
}

bool JSTestCallback::callbackWithSerializedScriptValueParam(PassRefPtr<SerializedScriptValue> srzParam, const String& strArg)
{
    if (!canInvokeCallback())
        return true;

    Ref<JSTestCallback> protect(*this);

    JSLockHolder lock(m_data->globalObject()->vm());

    ExecState* exec = m_data->globalObject()->globalExec();
    MarkedArgumentBuffer args;
    args.append(srzParam ? srzParam->deserialize(exec, m_data->globalObject(), 0) : jsNull());
    args.append(jsStringWithCache(exec, strArg));

    bool raisedException = false;
    m_data->invokeCallback(args, &raisedException);
    return !raisedException;
}

bool JSTestCallback::callbackWithStringList(PassRefPtr<DOMStringList> listParam)
{
    if (!canInvokeCallback())
        return true;

    Ref<JSTestCallback> protect(*this);

    JSLockHolder lock(m_data->globalObject()->vm());

    ExecState* exec = m_data->globalObject()->globalExec();
    MarkedArgumentBuffer args;
    args.append(toJS(exec, m_data->globalObject(), listParam));

    bool raisedException = false;
    m_data->invokeCallback(args, &raisedException);
    return !raisedException;
}

bool JSTestCallback::callbackWithBoolean(bool boolParam)
{
    if (!canInvokeCallback())
        return true;

    Ref<JSTestCallback> protect(*this);

    JSLockHolder lock(m_data->globalObject()->vm());

    ExecState* exec = m_data->globalObject()->globalExec();
    MarkedArgumentBuffer args;
    args.append(jsBoolean(boolParam));

    bool raisedException = false;
    m_data->invokeCallback(args, &raisedException);
    return !raisedException;
}

bool JSTestCallback::callbackRequiresThisToPass(int longParam, TestNode* testNodeParam)
{
    if (!canInvokeCallback())
        return true;

    Ref<JSTestCallback> protect(*this);

    JSLockHolder lock(m_data->globalObject()->vm());

    ExecState* exec = m_data->globalObject()->globalExec();
    MarkedArgumentBuffer args;
    args.append(toJS(exec, m_data->globalObject(), longParam));
    args.append(toJS(exec, m_data->globalObject(), testNodeParam));

    bool raisedException = false;
    m_data->invokeCallback(args, &raisedException);
    return !raisedException;
}

}

#endif // ENABLE(SQL_DATABASE)
