package com.example.minicommerce.payment.application;
import java.math.BigDecimal;import java.util.UUID;import org.springframework.stereotype.Component;
/** 本地确定性支付模拟器：decline/timeout/unknown token 用于故障实验，不连接真实资金系统。 */
@Component public class FakePaymentGateway implements PaymentGateway{public GatewayResult charge(UUID id,BigDecimal amount,String currency,String token){if("decline".equalsIgnoreCase(token))return GatewayResult.declined("模拟拒付");if("unknown".equalsIgnoreCase(token)||"timeout".equalsIgnoreCase(token))return GatewayResult.unknown("模拟响应丢失，不能断言支付未发生");return GatewayResult.success("fake_"+id.toString().replace("-","").substring(0,18));}public GatewayResult refund(UUID id,BigDecimal amount){return GatewayResult.success("refund_"+id.toString().substring(0,8));}}
