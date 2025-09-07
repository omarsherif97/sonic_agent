api_example = """
<api xmlns="http://ws.apache.org/ns/synapse" context="((api_context))" name="((service_name))">
    <resource methods="POST">
        <inSequence>
            <throttle id="group_id">
                <policy>
                    <wsp:Policy xmlns:wsp="http://schemas.xmlsoap.org/ws/2004/09/policy" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:id="WSO2MediatorThrottlingPolicy">
                        <throttle:MediatorThrottleAssertion xmlns:throttle="http://www.wso2.org/products/wso2commons/throttle">
                            <throttle:MaximumConcurrentAccess>0</throttle:MaximumConcurrentAccess>
                            <wsp:Policy>
                                <throttle:ID throttle:type="IP">other</throttle:ID>
                                <wsp:Policy>
                                    <throttle:Control>
                                        <wsp:Policy>
                                            <throttle:MaximumCount>50</throttle:MaximumCount>
                                            <throttle:UnitTime>1000</throttle:UnitTime>
                                            <throttle:ProhibitTimePeriod>0</throttle:ProhibitTimePeriod>
                                        </wsp:Policy>
                                    </throttle:Control>
                                </wsp:Policy>
                            </wsp:Policy>
                        </throttle:MediatorThrottleAssertion>
                    </wsp:Policy>
                </policy>
                <onReject>
                    <payloadFactory media-type="xml">
                        <format>
                            <ExternalServiceResponse xmlns="">
                                <EXTTxnID>$1</EXTTxnID>
                                <TransactionTimeStamp>$2</TransactionTimeStamp>
                                <Status>esb:1</Status>
                                <Message>Exceeding Rate Limit</Message>
                            </ExternalServiceResponse>
                        </format>
                        <args>
                            <arg evaluator="xml" expression="$body/ExternalServiceRequest/GLETxnID"/>
                            <arg evaluator="xml" expression="get-property('SYSTEM_DATE', 'yyyy-MM-dd HH:mm:ss.SSS')"/>
                        </args>
                    </payloadFactory>
                    <property name="HTTP_SC" scope="axis2" type="STRING" value="429"/>
                    <property description="MessageType" name="messageType" scope="axis2" type="STRING" value="application/xml"/>
                    <respond/>
                </onReject>
                <onAccept>
                    <log description="ExternalServiceRequestLog" level="full"/>
                    <sequence key="((service_name))-main-sequence-test"/>
                </onAccept>
            </throttle>
        </inSequence>
        <outSequence/>
        <faultSequence/>
    </resource>
</api>
"""

endpoint_example = """
<endpoint xmlns="http://ws.apache.org/ns/synapse" name="((service_name))">
    <http method="post" uri-template="((service_uri_template))">
        <timeout>
            <duration>30000</duration>
        </timeout>
        <suspendOnFailure>
            <initialDuration>-1</initialDuration>
            <progressionFactor>1.0</progressionFactor>
        </suspendOnFailure>
        <markForSuspension>
            <retriesBeforeSuspension>0</retriesBeforeSuspension>
        </markForSuspension>
    </http>
</endpoint>
"""

main_sequence_template = """
<?xml version="1.0" encoding="UTF-8"?>
<sequence name="(service_name)-main-sequence" trace="disable" xmlns="http://ws.apache.org/ns/synapse">
    <property expression="$body/ExternalServiceRequest/GLETxnID/text()" name="GLETxnID" scope="default" type="STRING"/>
    <property expression="$body/ExternalServiceRequest/DestinationAccountID/text()" name="refnum" scope="default" type="STRING"/>
    <property expression="$body/ExternalServiceRequest/DestinationAccountID/text()" name="referenceNumber" scope="default" type="STRING"/>
    <property expression="$body/ExternalServiceRequest/xparam/inquiry_key/text()" name="inquiry_key" scope="default" type="STRING"/>
    <property expression="$body/ExternalServiceRequest/xparam/service_id_aman/text()" name="ServiceCode" scope="default" type="STRING"/>
    <property expression="$body/ExternalServiceRequest/xparam/terminalId/text()" name="terminal" scope="default" type="STRING"/>
    <property expression="$body/ExternalServiceRequest/xparam/productCode/text()" name="productCode" scope="default" type="STRING"/>
        <property name="propertyFilePath" value="dev.properties"/>
    </class>
    <switch source="$ctx:ServiceCode">
        <case regex="(service-code)">
            <sequence key="(service_name)-inquiry_request"/>
            <sequence key="(service_name)-inquiry-response"/>
        </case>
        <default>
            <payloadFactory media-type="xml">
                <format>
                    <ExternalServiceResponse xmlns="">
                        <EXTTxnID/>
                        <TransactionTimeStamp>$1</TransactionTimeStamp>
                        <Status>esb:INVALID_SEQUENCE</Status>
                        <Message>ESB invalid sequence</Message>
                    </ExternalServiceResponse>
                </format>
                <args>
                    <arg evaluator="xml" expression="get-property('SYSTEM_DATE', 'yyyy-MM-dd HH:mm:ss.SSS')"/>
                </args>
            </payloadFactory>
            <property description="MessageType" name="messageType" scope="axis2" type="STRING" value="application/xml"/>
            <log description="LogResponse" level="full"/>
            <respond/>
        </default>
    </switch>
    <respond/>
</sequence>
"""

wso2_custom_exception_example = """
<?xml version="1.0" encoding="UTF-8"?>
<sequence name="((service_name))-custom-exception" trace="disable" xmlns="http://ws.apache.org/ns/synapse">
    <log description="Aman Custom Exception" level="custom">
        <property name="Aman_Custom_Exception" value="Starting Aman ((service_name))-custom-exception"/>
    </log>
    <payloadFactory media-type="xml">
        <format>
            <ExternalServiceResponse xmlns="">
                <EXTTxnID>$1</EXTTxnID>
                <TransactionTimeStamp>$2</TransactionTimeStamp>
                <Status>$3</Status>
                <Message>$4</Message>
            </ExternalServiceResponse>
        </format>
        <args>
            <arg evaluator="xml" expression="get-property('GLETxnID')"/>
            <arg evaluator="xml" expression="get-property('SYSTEM_DATE', 'yyyy-MM-dd HH:mm:ss.SSS')"/>
            <arg evaluator="xml" expression="get-property('exceptionCode')"/>
            <arg evaluator="xml" expression="get-property('exceptionMessage')"/>
        </args>
    </payloadFactory>
    <property name="HTTP_SC" scope="axis2" type="STRING" value="400"/>
    <property description="MessageType" name="messageType" scope="axis2" type="STRING" value="application/xml"/>
    <log description="LogErrorResponse" level="full"/>
    <respond/>
</sequence>
"""
