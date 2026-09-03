package com.example.minicommerce.shared.security;

import com.example.minicommerce.shared.web.RateLimitFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

/**
 * 后端 API 的安全配置。
 *
 * <p><strong>作用：</strong>规定哪些接口可以匿名访问、哪些接口必须登录、JWT 过滤器和限流过滤器按什么顺序执行，以及密码使用什么哈希算法。
 *
 * <p><strong>大白话：</strong>这里像 API 大门的门禁规则。请求先经过门禁，再进入 Controller。
 *
 * <p><strong>为什么当前关闭 CSRF：</strong>本项目 API 使用请求头中的 Bearer Token，不依赖浏览器自动携带的登录 Cookie。 如果以后改成
 * Session Cookie，必须重新评估并启用 CSRF Token，不能照抄当前配置。
 *
 * <p><strong>对应文档：</strong> {@code 05_auth_security/01_Session_Cookie_Token.md}、 {@code
 * 05_auth_security/02_RBAC与对象级权限.md}、 {@code 05_auth_security/03_Web常见攻击.md}、 {@code
 * mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md}。
 */
// @Configuration：告诉 Spring，这个类主要集中声明系统需要的 Bean 和技术配置。
@Configuration
// @EnableMethodSecurity：打开方法级权限功能，使 @PreAuthorize 等注解可以生效。
@EnableMethodSecurity
public class SecurityConfiguration {

    /**
     * 构建 HTTP 安全过滤链。
     *
     * <p>可以按“关闭或开启安全能力 → 配置登录状态 → 配置异常响应 → 配置 URL 权限 → 安排过滤器顺序”阅读。
     */
    // @Bean：把这个方法返回的 SecurityFilterChain 交给 Spring 管理。
    @Bean
    SecurityFilterChain filterChain(
            HttpSecurity http,
            JwtAuthenticationFilter jwt,
            RateLimitFilter rateLimit,
            ApiSecurityHandlers handlers)
            throws Exception {
        return http
                // 当前使用 Bearer Token；若改成 Cookie 登录，不能继续机械关闭 CSRF。
                .csrf(csrf -> csrf.disable())
                // STATELESS 表示服务端不保存 HTTP Session，每次请求都要携带并验证 Token。
                .sessionManagement(
                        session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                // 未登录返回 401；已经登录但无权限返回 403。统一由 handlers 输出 JSON。
                .exceptionHandling(
                        exceptions ->
                                exceptions
                                        .authenticationEntryPoint(handlers)
                                        .accessDeniedHandler(handlers))
                .authorizeHttpRequests(
                        authorization ->
                                authorization
                                        // 健康检查和基本信息允许部署平台匿名访问。
                                        .requestMatchers("/actuator/health/**", "/actuator/info")
                                        .permitAll()
                                        // 注册和登录必须允许未登录用户访问。
                                        .requestMatchers("/api/auth/**")
                                        .permitAll()
                                        // 浏览公开商品不需要登录。
                                        .requestMatchers(HttpMethod.GET, "/api/products/**")
                                        .permitAll()
                                        // 支付平台回调不携带用户 JWT，但必须在业务层验签和去重。
                                        .requestMatchers("/api/payments/webhooks/**")
                                        .permitAll()
                                        // 其他请求默认要求已经通过认证。
                                        .anyRequest()
                                        .authenticated())
                // 先解析 JWT，再让后续 Spring Security 逻辑知道当前用户是谁。
                .addFilterBefore(jwt, UsernamePasswordAuthenticationFilter.class)
                // 限流过滤器放在 JWT 后，可以根据已解析用户或请求信息做更准确的限流。
                .addFilterAfter(rateLimit, JwtAuthenticationFilter.class)
                .build();
    }

    /**
     * 密码编码器。
     *
     * <p>BCrypt 保存的是密码哈希，不是可逆加密。登录时对用户输入执行校验，不会把数据库中的哈希“解密回密码”。
     */
    @Bean
    PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }
}
