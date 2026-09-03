package com.example.minicommerce.support;

import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

/**
 * PostgreSQL 集成测试的共同基础类。
 *
 * <p><strong>作用：</strong>为继承它的测试类启动真实 PostgreSQL 容器，并把动态 JDBC 地址交给 Spring Boot。
 * 这样测试验证的是 PostgreSQL、Flyway、JPA 和真实事务，而不是只验证内存数据库。
 *
 * <p><strong>为什么加入 {@link DirtiesContext}：</strong>{@link Container} 的静态容器按测试类启动和停止，
 * 但 Spring 默认会在不同测试类之间复用应用上下文。如果第一个容器停止后仍复用旧连接池，第二个测试就会继续访问已经关闭的旧端口。
 * 每个集成测试类结束后关闭对应 Spring 上下文，可以让下一类测试使用自己的新容器地址，避免“容器已经换了，连接池仍指向旧端口”。
 *
 * <p><strong>本地没有 Docker 时：</strong>{@code disabledWithoutDocker = true} 会明确跳过这些容器测试，
 * 不会把“没有运行”误报成“已经通过”。
 *
 * <p><strong>对应文档：</strong> {@code 03_testing/05_集成测试与Testcontainers.md}、 {@code
 * 04_database_postgresql/04_事务与Spring边界.md}、 {@code 04_database_postgresql/05_并发_锁与库存超卖.md}。
 */
// @Testcontainers：让 JUnit 管理 @Container，并在没有 Docker 时跳过容器测试。
@Testcontainers(disabledWithoutDocker = true)
// @SpringBootTest：启动完整 Spring 应用上下文，验证真实组件组合。
@SpringBootTest
@ActiveProfiles("test")
// 每个测试类结束后关闭旧 Spring 上下文，防止连接池继续指向已停止的容器端口。
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_CLASS)
public abstract class AbstractPostgresIT {

    // static @Container：同一个测试类中的所有测试方法共享一个 PostgreSQL 容器。
    @Container
    static final PostgreSQLContainer<?> POSTGRES =
            new PostgreSQLContainer<>("postgres:17-alpine")
                    .withDatabaseName("commerce")
                    .withUsername("commerce")
                    .withPassword("commerce");

    /**
     * 容器启动后，把随机映射的 JDBC 地址、用户名和密码写入 Spring 测试配置。
     *
     * <p>Outbox 后台发布器在集成测试中关闭，避免测试结果依赖 RabbitMQ 和定时任务。
     */
    @DynamicPropertySource
    static void registerDynamicProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", POSTGRES::getJdbcUrl);
        registry.add("spring.datasource.username", POSTGRES::getUsername);
        registry.add("spring.datasource.password", POSTGRES::getPassword);
        registry.add("app.outbox.publisher-enabled", () -> "false");
    }
}
