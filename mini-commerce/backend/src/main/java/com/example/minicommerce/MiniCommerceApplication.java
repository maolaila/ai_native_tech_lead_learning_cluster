package com.example.minicommerce;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Mini Commerce 后端的启动入口。
 *
 * <p><strong>作用：</strong>启动 Spring Boot，扫描项目组件，读取类型化配置，并开启定时任务。
 *
 * <p><strong>为什么使用模块化单体：</strong>订单、库存和优惠券目前需要共享一个数据库事务。先在一个应用中把业务边界、测试和可观测性做好，
 * 比一开始就拆成很多微服务更容易保证正确性。
 *
 * <p><strong>对应文档：</strong> {@code 00_start/02_长期项目_Mini_Commerce.md}、 {@code
 * 02_backend_spring/01_请求生命周期与IoC_DI.md}、 {@code 08_runtime_deployment/04_进程_资源与优雅关闭.md}。
 *
 * <p><strong>小白补充：</strong>常见注解的通俗解释见 {@code mini-commerce/docs/SPRING-JAVA-ANNOTATIONS.md}。
 */
// @SpringBootApplication 可以先理解成“从这里启动 Spring Boot，并启用常用自动配置”。
@SpringBootApplication
// @ConfigurationPropertiesScan 让 Spring 找到 @ConfigurationProperties 配置类并给它们填值。
@ConfigurationPropertiesScan
// @EnableScheduling 打开定时任务功能，OutboxPublisher 中的 @Scheduled 才会按间隔运行。
@EnableScheduling
public class MiniCommerceApplication {

    /** JVM 从 main 方法开始执行；SpringApplication.run 会创建并启动整个 Spring 应用。 */
    public static void main(String[] args) {
        SpringApplication.run(MiniCommerceApplication.class, args);
    }
}
