package com.example.minicommerce.shared.config;

import java.time.Clock;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** 对应文档：03_testing/03_后端单元测试.md。注入 Clock 后，过期边界测试不依赖真实时间。 */
@Configuration
public class ClockConfiguration {
    @Bean
    Clock clock() {
        return Clock.systemUTC();
    }
}
