package com.example.minicommerce;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * 完整工程的启动入口。
 *
 * <p>对应文档：00_start/02_长期项目_Mini_Commerce.md、 08_runtime_deployment/04_进程_资源与优雅关闭.md。
 *
 * <p>采用模块化单体而不是一开始拆微服务，因为订单、库存、优惠券当前共享一个强一致事务边界； 先把边界、测试和可观测性做好，再根据真实负载决定是否拆分。
 */
@SpringBootApplication
@ConfigurationPropertiesScan
@EnableScheduling
public class MiniCommerceApplication {
    public static void main(String[] args) {
        SpringApplication.run(MiniCommerceApplication.class, args);
    }
}
