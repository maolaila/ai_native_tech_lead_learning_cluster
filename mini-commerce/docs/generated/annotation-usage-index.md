# Java 注解使用位置索引

> 本文件由 `tools/generate_annotation_usage_index.py` 自动生成，仅统计代码中的注解，不统计注释和字符串提及。
> 注解作用的通俗解释见 [`SPRING-JAVA-ANNOTATIONS.md`](../SPRING-JAVA-ANNOTATIONS.md)。

- 注解种类：73
- 注解出现次数：620

## 使用方法

1. 先在注解词典中看它的通俗解释；
2. 再从本页打开真实源码；
3. 只观察它贴在类、方法、参数还是字段上；
4. 思考去掉它后，程序会发生什么变化。

## `@ActiveProfiles`

出现 1 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java`](../../backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java#L32)：首次出现在第 32 行

## `@AnalyzeClasses`

出现 1 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/ArchitectureTest.java`](../../backend/src/test/java/com/example/minicommerce/ArchitectureTest.java#L18)：首次出现在第 18 行

## `@ArchTest`

出现 2 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/ArchitectureTest.java`](../../backend/src/test/java/com/example/minicommerce/ArchitectureTest.java#L22)：首次出现在第 22 行

## `@AutoConfigureMockMvc`

出现 2 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java`](../../backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java#L35)：首次出现在第 35 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/LearningReadinessIT.java`](../../backend/src/test/java/com/example/minicommerce/LearningReadinessIT.java#L35)：首次出现在第 35 行

## `@Autowired`

出现 38 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java`](../../backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java#L37)：首次出现在第 37 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/LearningReadinessIT.java`](../../backend/src/test/java/com/example/minicommerce/LearningReadinessIT.java#L37)：首次出现在第 37 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/inventory/InventoryConcurrencyIT.java`](../../backend/src/test/java/com/example/minicommerce/inventory/InventoryConcurrencyIT.java#L27)：首次出现在第 27 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/order/CreateOrderIT.java`](../../backend/src/test/java/com/example/minicommerce/order/CreateOrderIT.java#L31)：首次出现在第 31 行

## `@Bean`

出现 23 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/config/RabbitTopology.java`](../../backend/src/main/java/com/example/minicommerce/messaging/config/RabbitTopology.java#L37)：首次出现在第 37 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/config/ClockConfiguration.java`](../../backend/src/main/java/com/example/minicommerce/shared/config/ClockConfiguration.java#L10)：首次出现在第 10 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/SecurityConfiguration.java`](../../backend/src/main/java/com/example/minicommerce/shared/security/SecurityConfiguration.java#L41)：首次出现在第 41 行

## `@BeforeEach`

出现 3 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java`](../../backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java#L56)：首次出现在第 56 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/LearningReadinessIT.java`](../../backend/src/test/java/com/example/minicommerce/LearningReadinessIT.java#L51)：首次出现在第 51 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/order/CreateOrderIT.java`](../../backend/src/test/java/com/example/minicommerce/order/CreateOrderIT.java#L41)：首次出现在第 41 行

## `@Column`

出现 124 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java`](../../backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java#L28)：首次出现在第 28 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java`](../../backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java#L26)：首次出现在第 26 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java`](../../backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java#L45)：首次出现在第 45 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java`](../../backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java#L30)：首次出现在第 30 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenEntity.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenEntity.java#L24)：首次出现在第 24 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java#L20)：首次出现在第 20 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryEntity.java`](../../backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryEntity.java#L20)：首次出现在第 20 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxEventEntity.java`](../../backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxEventEntity.java#L26)：首次出现在第 26 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/infrastructure/NotificationEntity.java`](../../backend/src/main/java/com/example/minicommerce/notification/infrastructure/NotificationEntity.java#L22)：首次出现在第 22 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/infrastructure/PointsLedgerEntity.java`](../../backend/src/main/java/com/example/minicommerce/notification/infrastructure/PointsLedgerEntity.java#L29)：首次出现在第 29 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/IdempotencyRecordEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/IdempotencyRecordEntity.java#L27)：首次出现在第 27 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java#L26)：首次出现在第 26 行
- 其余 6 个文件可在 IDE 中全局搜索 `@Column`

## `@Component`

出现 16 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/application/ProductCacheInvalidationConsumer.java`](../../backend/src/main/java/com/example/minicommerce/catalog/application/ProductCacheInvalidationConsumer.java#L20)：首次出现在第 20 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/application/DemoDataInitializer.java`](../../backend/src/main/java/com/example/minicommerce/identity/application/DemoDataInitializer.java#L24)：首次出现在第 24 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/OrderLifecycleConsumer.java`](../../backend/src/main/java/com/example/minicommerce/messaging/application/OrderLifecycleConsumer.java#L17)：首次出现在第 17 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/OutboxPublisher.java`](../../backend/src/main/java/com/example/minicommerce/messaging/application/OutboxPublisher.java#L33)：首次出现在第 33 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/application/OrderPaidConsumers.java`](../../backend/src/main/java/com/example/minicommerce/notification/application/OrderPaidConsumers.java#L30)：首次出现在第 30 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/observability/CommerceHealthIndicator.java`](../../backend/src/main/java/com/example/minicommerce/observability/CommerceHealthIndicator.java#L13)：首次出现在第 13 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/IdempotencyLock.java`](../../backend/src/main/java/com/example/minicommerce/order/application/IdempotencyLock.java#L11)：首次出现在第 11 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/RequestFingerprint.java`](../../backend/src/main/java/com/example/minicommerce/order/application/RequestFingerprint.java#L19)：首次出现在第 19 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/application/FakePaymentGateway.java`](../../backend/src/main/java/com/example/minicommerce/payment/application/FakePaymentGateway.java#L13)：首次出现在第 13 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/application/WebhookSignature.java`](../../backend/src/main/java/com/example/minicommerce/payment/application/WebhookSignature.java#L22)：首次出现在第 22 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/ApiSecurityHandlers.java`](../../backend/src/main/java/com/example/minicommerce/shared/security/ApiSecurityHandlers.java#L28)：首次出现在第 28 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/CurrentUser.java`](../../backend/src/main/java/com/example/minicommerce/shared/security/CurrentUser.java#L13)：首次出现在第 13 行
- 其余 4 个文件可在 IDE 中全局搜索 `@Component`

## `@ConditionalOnProperty`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/OutboxPublisher.java`](../../backend/src/main/java/com/example/minicommerce/messaging/application/OutboxPublisher.java#L35)：首次出现在第 35 行

## `@Configuration`

出现 3 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/config/RabbitTopology.java`](../../backend/src/main/java/com/example/minicommerce/messaging/config/RabbitTopology.java#L27)：首次出现在第 27 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/config/ClockConfiguration.java`](../../backend/src/main/java/com/example/minicommerce/shared/config/ClockConfiguration.java#L8)：首次出现在第 8 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/SecurityConfiguration.java`](../../backend/src/main/java/com/example/minicommerce/shared/security/SecurityConfiguration.java#L30)：首次出现在第 30 行

## `@ConfigurationProperties`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/config/AppProperties.java`](../../backend/src/main/java/com/example/minicommerce/shared/config/AppProperties.java#L30)：首次出现在第 30 行

## `@ConfigurationPropertiesScan`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/MiniCommerceApplication.java`](../../backend/src/main/java/com/example/minicommerce/MiniCommerceApplication.java#L24)：首次出现在第 24 行

## `@Container`

出现 1 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java`](../../backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java#L38)：首次出现在第 38 行

## `@DecimalMin`

出现 2 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java#L24)：首次出现在第 24 行

## `@DeleteMapping`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/api/CartController.java`](../../backend/src/main/java/com/example/minicommerce/cart/api/CartController.java#L42)：首次出现在第 42 行

## `@Digits`

出现 2 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java#L24)：首次出现在第 24 行

## `@DirtiesContext`

出现 1 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java`](../../backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java#L34)：首次出现在第 34 行

## `@DynamicPropertySource`

出现 1 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java`](../../backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java#L50)：首次出现在第 50 行

## `@Email`

出现 2 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/api/AuthDtos.java`](../../backend/src/main/java/com/example/minicommerce/identity/api/AuthDtos.java#L22)：首次出现在第 22 行

## `@EnableMethodSecurity`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/SecurityConfiguration.java`](../../backend/src/main/java/com/example/minicommerce/shared/security/SecurityConfiguration.java#L32)：首次出现在第 32 行

## `@EnableScheduling`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/MiniCommerceApplication.java`](../../backend/src/main/java/com/example/minicommerce/MiniCommerceApplication.java#L26)：首次出现在第 26 行

## `@Entity`

出现 17 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java`](../../backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java#L16)：首次出现在第 16 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java`](../../backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java#L17)：首次出现在第 17 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java`](../../backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java#L28)：首次出现在第 28 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java`](../../backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java#L18)：首次出现在第 18 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenEntity.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenEntity.java#L17)：首次出现在第 17 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java#L11)：首次出现在第 11 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryEntity.java`](../../backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryEntity.java#L16)：首次出现在第 16 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxEventEntity.java`](../../backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxEventEntity.java#L17)：首次出现在第 17 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/infrastructure/NotificationEntity.java`](../../backend/src/main/java/com/example/minicommerce/notification/infrastructure/NotificationEntity.java#L17)：首次出现在第 17 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/infrastructure/PointsLedgerEntity.java`](../../backend/src/main/java/com/example/minicommerce/notification/infrastructure/PointsLedgerEntity.java#L17)：首次出现在第 17 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/IdempotencyRecordEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/IdempotencyRecordEntity.java#L17)：首次出现在第 17 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java#L16)：首次出现在第 16 行
- 其余 5 个文件可在 IDE 中全局搜索 `@Entity`

## `@Enumerated`

出现 6 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java`](../../backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java#L46)：首次出现在第 46 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java#L29)：首次出现在第 29 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java#L32)：首次出现在第 32 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptEntity.java`](../../backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptEntity.java#L41)：首次出现在第 41 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/CouponEntity.java`](../../backend/src/main/java/com/example/minicommerce/promotion/infrastructure/CouponEntity.java#L30)：首次出现在第 30 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponEntity.java`](../../backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponEntity.java#L35)：首次出现在第 35 行

## `@ExceptionHandler`

出现 12 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/error/GlobalExceptionHandler.java`](../../backend/src/main/java/com/example/minicommerce/shared/error/GlobalExceptionHandler.java#L39)：首次出现在第 39 行

## `@GeneratedValue`

出现 8 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java`](../../backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java#L25)：首次出现在第 25 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java`](../../backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java#L23)：首次出现在第 23 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java`](../../backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java#L41)：首次出现在第 41 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java`](../../backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java#L27)：首次出现在第 27 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java#L17)：首次出现在第 17 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/infrastructure/PointsLedgerEntity.java`](../../backend/src/main/java/com/example/minicommerce/notification/infrastructure/PointsLedgerEntity.java#L26)：首次出现在第 26 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/CouponEntity.java`](../../backend/src/main/java/com/example/minicommerce/promotion/infrastructure/CouponEntity.java#L24)：首次出现在第 24 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponEntity.java`](../../backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponEntity.java#L26)：首次出现在第 26 行

## `@GetMapping`

出现 7 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/api/CartController.java`](../../backend/src/main/java/com/example/minicommerce/cart/api/CartController.java#L32)：首次出现在第 32 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java#L44)：首次出现在第 44 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java`](../../backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java#L28)：首次出现在第 28 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/api/NotificationController.java`](../../backend/src/main/java/com/example/minicommerce/notification/api/NotificationController.java#L35)：首次出现在第 35 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderController.java#L77)：首次出现在第 77 行

## `@Id`

出现 17 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java`](../../backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java#L24)：首次出现在第 24 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java`](../../backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java#L22)：首次出现在第 22 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java`](../../backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java#L39)：首次出现在第 39 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java`](../../backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java#L26)：首次出现在第 26 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenEntity.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenEntity.java#L22)：首次出现在第 22 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java#L16)：首次出现在第 16 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryEntity.java`](../../backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryEntity.java#L19)：首次出现在第 19 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxEventEntity.java`](../../backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxEventEntity.java#L25)：首次出现在第 25 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/infrastructure/NotificationEntity.java`](../../backend/src/main/java/com/example/minicommerce/notification/infrastructure/NotificationEntity.java#L20)：首次出现在第 20 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/infrastructure/PointsLedgerEntity.java`](../../backend/src/main/java/com/example/minicommerce/notification/infrastructure/PointsLedgerEntity.java#L25)：首次出现在第 25 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/IdempotencyRecordEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/IdempotencyRecordEntity.java#L25)：首次出现在第 25 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java#L24)：首次出现在第 24 行
- 其余 5 个文件可在 IDE 中全局搜索 `@Id`

## `@Index`

出现 8 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java`](../../backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java#L20)：首次出现在第 20 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java`](../../backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java#L22)：首次出现在第 22 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenEntity.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenEntity.java#L20)：首次出现在第 20 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxEventEntity.java`](../../backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxEventEntity.java#L21)：首次出现在第 21 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java#L20)：首次出现在第 20 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/CouponEntity.java`](../../backend/src/main/java/com/example/minicommerce/promotion/infrastructure/CouponEntity.java#L21)：首次出现在第 21 行

## `@JdbcTypeCode`

出现 3 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java`](../../backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java#L43)：首次出现在第 43 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java#L46)：首次出现在第 46 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptEntity.java`](../../backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptEntity.java#L49)：首次出现在第 49 行

## `@Lock`

出现 6 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenRepository.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenRepository.java#L19)：首次出现在第 19 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java`](../../backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java#L65)：首次出现在第 65 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderRepository.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderRepository.java#L20)：首次出现在第 20 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptRepository.java`](../../backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptRepository.java#L26)：首次出现在第 26 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponRepository.java`](../../backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponRepository.java#L19)：首次出现在第 19 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/refund/infrastructure/RefundRepository.java`](../../backend/src/main/java/com/example/minicommerce/refund/infrastructure/RefundRepository.java#L23)：首次出现在第 23 行

## `@MappedSuperclass`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/persistence/BaseEntity.java`](../../backend/src/main/java/com/example/minicommerce/shared/persistence/BaseEntity.java#L22)：首次出现在第 22 行

## `@MockitoBean`

出现 2 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java`](../../backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java#L47)：首次出现在第 47 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/LearningReadinessIT.java`](../../backend/src/test/java/com/example/minicommerce/LearningReadinessIT.java#L47)：首次出现在第 47 行

## `@Modifying`

出现 4 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java`](../../backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java#L34)：首次出现在第 34 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptRepository.java`](../../backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptRepository.java#L30)：首次出现在第 30 行

## `@NotBlank`

出现 12 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java#L21)：首次出现在第 21 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/api/AuthDtos.java`](../../backend/src/main/java/com/example/minicommerce/identity/api/AuthDtos.java#L22)：首次出现在第 22 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java`](../../backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java#L61)：首次出现在第 61 行

## `@NotEmpty`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java#L23)：首次出现在第 23 行

## `@NotNull`

出现 6 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java#L23)：首次出现在第 23 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java#L23)：首次出现在第 23 行

## `@Order`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/web/CorrelationIdFilter.java`](../../backend/src/main/java/com/example/minicommerce/shared/web/CorrelationIdFilter.java#L20)：首次出现在第 20 行

## `@Override`

出现 14 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/application/DemoDataInitializer.java`](../../backend/src/main/java/com/example/minicommerce/identity/application/DemoDataInitializer.java#L49)：首次出现在第 49 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/ApiSecurityHandlers.java`](../../backend/src/main/java/com/example/minicommerce/shared/security/ApiSecurityHandlers.java#L38)：首次出现在第 38 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/JwtAuthenticationFilter.java`](../../backend/src/main/java/com/example/minicommerce/shared/security/JwtAuthenticationFilter.java#L35)：首次出现在第 35 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/security/UserPrincipal.java`](../../backend/src/main/java/com/example/minicommerce/shared/security/UserPrincipal.java#L27)：首次出现在第 27 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/transaction/AfterCommitExecutor.java`](../../backend/src/main/java/com/example/minicommerce/shared/transaction/AfterCommitExecutor.java#L27)：首次出现在第 27 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/web/CorrelationIdFilter.java`](../../backend/src/main/java/com/example/minicommerce/shared/web/CorrelationIdFilter.java#L24)：首次出现在第 24 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/web/RateLimitFilter.java`](../../backend/src/main/java/com/example/minicommerce/shared/web/RateLimitFilter.java#L31)：首次出现在第 31 行

## `@PageableDefault`

出现 2 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java#L46)：首次出现在第 46 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderController.java#L88)：首次出现在第 88 行

## `@Param`

出现 14 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java`](../../backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java#L41)：首次出现在第 41 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderRepository.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderRepository.java#L22)：首次出现在第 22 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptRepository.java`](../../backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptRepository.java#L28)：首次出现在第 28 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponRepository.java`](../../backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponRepository.java#L22)：首次出现在第 22 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/refund/infrastructure/RefundRepository.java`](../../backend/src/main/java/com/example/minicommerce/refund/infrastructure/RefundRepository.java#L25)：首次出现在第 25 行

## `@PathVariable`

出现 11 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/api/CartController.java`](../../backend/src/main/java/com/example/minicommerce/cart/api/CartController.java#L38)：首次出现在第 38 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java#L52)：首次出现在第 52 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java`](../../backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java#L30)：首次出现在第 30 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderController.java#L80)：首次出现在第 80 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java`](../../backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java#L41)：首次出现在第 41 行

## `@Pattern`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java#L25)：首次出现在第 25 行

## `@Positive`

出现 3 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/api/CartController.java`](../../backend/src/main/java/com/example/minicommerce/cart/api/CartController.java#L48)：首次出现在第 48 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java#L26)：首次出现在第 26 行

## `@PositiveOrZero`

出现 2 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java#L26)：首次出现在第 26 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java`](../../backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java#L41)：首次出现在第 41 行

## `@PostMapping`

出现 11 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java#L56)：首次出现在第 56 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java`](../../backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java#L24)：首次出现在第 24 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderController.java#L65)：首次出现在第 65 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java`](../../backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java#L39)：首次出现在第 39 行

## `@PreAuthorize`

出现 5 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/application/ProductService.java`](../../backend/src/main/java/com/example/minicommerce/catalog/application/ProductService.java#L80)：首次出现在第 80 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java`](../../backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java#L29)：首次出现在第 29 行

## `@PrePersist`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/persistence/BaseEntity.java`](../../backend/src/main/java/com/example/minicommerce/shared/persistence/BaseEntity.java#L37)：首次出现在第 37 行

## `@PreUpdate`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/persistence/BaseEntity.java`](../../backend/src/main/java/com/example/minicommerce/shared/persistence/BaseEntity.java#L47)：首次出现在第 47 行

## `@Profile`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/application/DemoDataInitializer.java`](../../backend/src/main/java/com/example/minicommerce/identity/application/DemoDataInitializer.java#L25)：首次出现在第 25 行

## `@PutMapping`

出现 3 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/api/CartController.java`](../../backend/src/main/java/com/example/minicommerce/cart/api/CartController.java#L37)：首次出现在第 37 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java#L62)：首次出现在第 62 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java`](../../backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java#L34)：首次出现在第 34 行

## `@Query`

出现 9 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java`](../../backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryRepository.java#L36)：首次出现在第 36 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderRepository.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderRepository.java#L21)：首次出现在第 21 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptRepository.java`](../../backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptRepository.java#L27)：首次出现在第 27 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponRepository.java`](../../backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponRepository.java#L20)：首次出现在第 20 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/refund/infrastructure/RefundRepository.java`](../../backend/src/main/java/com/example/minicommerce/refund/infrastructure/RefundRepository.java#L24)：首次出现在第 24 行

## `@RabbitListener`

出现 4 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/application/ProductCacheInvalidationConsumer.java`](../../backend/src/main/java/com/example/minicommerce/catalog/application/ProductCacheInvalidationConsumer.java#L33)：首次出现在第 33 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/OrderLifecycleConsumer.java`](../../backend/src/main/java/com/example/minicommerce/messaging/application/OrderLifecycleConsumer.java#L30)：首次出现在第 30 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/application/OrderPaidConsumers.java`](../../backend/src/main/java/com/example/minicommerce/notification/application/OrderPaidConsumers.java#L57)：首次出现在第 57 行

## `@Repository`

出现 2 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxJdbcRepository.java`](../../backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxJdbcRepository.java#L15)：首次出现在第 15 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentWebhookRepository.java`](../../backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentWebhookRepository.java#L16)：首次出现在第 16 行

## `@RequestBody`

出现 11 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/api/CartController.java`](../../backend/src/main/java/com/example/minicommerce/cart/api/CartController.java#L38)：首次出现在第 38 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java#L58)：首次出现在第 58 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java`](../../backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java#L26)：首次出现在第 26 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java`](../../backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java#L37)：首次出现在第 37 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderController.java#L72)：首次出现在第 72 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java`](../../backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java#L43)：首次出现在第 43 行

## `@RequestHeader`

出现 4 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderController.java#L70)：首次出现在第 70 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java`](../../backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java#L42)：首次出现在第 42 行

## `@RequestMapping`

出现 7 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/api/CartController.java`](../../backend/src/main/java/com/example/minicommerce/cart/api/CartController.java#L22)：首次出现在第 22 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java#L34)：首次出现在第 34 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java`](../../backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java#L16)：首次出现在第 16 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java`](../../backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java#L20)：首次出现在第 20 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/api/NotificationController.java`](../../backend/src/main/java/com/example/minicommerce/notification/api/NotificationController.java#L23)：首次出现在第 23 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderController.java#L40)：首次出现在第 40 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java`](../../backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java#L24)：首次出现在第 24 行

## `@ResponseStatus`

出现 5 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/api/CartController.java`](../../backend/src/main/java/com/example/minicommerce/cart/api/CartController.java#L43)：首次出现在第 43 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java#L57)：首次出现在第 57 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java`](../../backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java#L25)：首次出现在第 25 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderController.java#L67)：首次出现在第 67 行

## `@RestController`

出现 7 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/api/CartController.java`](../../backend/src/main/java/com/example/minicommerce/cart/api/CartController.java#L21)：首次出现在第 21 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java#L33)：首次出现在第 33 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java`](../../backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java#L15)：首次出现在第 15 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java`](../../backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java#L19)：首次出现在第 19 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/api/NotificationController.java`](../../backend/src/main/java/com/example/minicommerce/notification/api/NotificationController.java#L22)：首次出现在第 22 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderController.java#L38)：首次出现在第 38 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java`](../../backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java#L23)：首次出现在第 23 行

## `@RestControllerAdvice`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/shared/error/GlobalExceptionHandler.java`](../../backend/src/main/java/com/example/minicommerce/shared/error/GlobalExceptionHandler.java#L33)：首次出现在第 33 行

## `@Scheduled`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/OutboxPublisher.java`](../../backend/src/main/java/com/example/minicommerce/messaging/application/OutboxPublisher.java#L67)：首次出现在第 67 行

## `@Service`

出现 21 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/audit/application/AuditService.java`](../../backend/src/main/java/com/example/minicommerce/audit/application/AuditService.java#L14)：首次出现在第 14 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/application/CartService.java`](../../backend/src/main/java/com/example/minicommerce/cart/application/CartService.java#L26)：首次出现在第 26 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/application/ProductCacheService.java`](../../backend/src/main/java/com/example/minicommerce/catalog/application/ProductCacheService.java#L28)：首次出现在第 28 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/application/ProductService.java`](../../backend/src/main/java/com/example/minicommerce/catalog/application/ProductService.java#L31)：首次出现在第 31 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/application/AuthService.java`](../../backend/src/main/java/com/example/minicommerce/identity/application/AuthService.java#L26)：首次出现在第 26 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/application/InventoryService.java`](../../backend/src/main/java/com/example/minicommerce/inventory/application/InventoryService.java#L14)：首次出现在第 14 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/OutboxService.java`](../../backend/src/main/java/com/example/minicommerce/messaging/application/OutboxService.java#L11)：首次出现在第 11 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/ProcessedMessageService.java`](../../backend/src/main/java/com/example/minicommerce/messaging/application/ProcessedMessageService.java#L13)：首次出现在第 13 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/application/NotificationQueryService.java`](../../backend/src/main/java/com/example/minicommerce/notification/application/NotificationQueryService.java#L23)：首次出现在第 23 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java`](../../backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java#L52)：首次出现在第 52 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/OrderCommandService.java`](../../backend/src/main/java/com/example/minicommerce/order/application/OrderCommandService.java#L28)：首次出现在第 28 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/OrderQueryService.java`](../../backend/src/main/java/com/example/minicommerce/order/application/OrderQueryService.java#L23)：首次出现在第 23 行
- 其余 9 个文件可在 IDE 中全局搜索 `@Service`

## `@Size`

出现 9 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductDtos.java#L21)：首次出现在第 21 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/api/AuthDtos.java`](../../backend/src/main/java/com/example/minicommerce/identity/api/AuthDtos.java#L23)：首次出现在第 23 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java#L23)：首次出现在第 23 行

## `@SpringBootApplication`

出现 1 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/MiniCommerceApplication.java`](../../backend/src/main/java/com/example/minicommerce/MiniCommerceApplication.java#L22)：首次出现在第 22 行

## `@SpringBootTest`

出现 1 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java`](../../backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java#L31)：首次出现在第 31 行

## `@SuppressWarnings`

出现 3 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/InfrastructureReadinessTest.java`](../../backend/src/test/java/com/example/minicommerce/InfrastructureReadinessTest.java#L42)：首次出现在第 42 行

## `@Table`

出现 17 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java`](../../backend/src/main/java/com/example/minicommerce/audit/infrastructure/AuditLogEntity.java#L17)：首次出现在第 17 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java`](../../backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java#L18)：首次出现在第 18 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java`](../../backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java#L30)：首次出现在第 30 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java`](../../backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java#L19)：首次出现在第 19 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenEntity.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/RefreshTokenEntity.java#L18)：首次出现在第 18 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java#L12)：首次出现在第 12 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryEntity.java`](../../backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryEntity.java#L17)：首次出现在第 17 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxEventEntity.java`](../../backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxEventEntity.java#L18)：首次出现在第 18 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/infrastructure/NotificationEntity.java`](../../backend/src/main/java/com/example/minicommerce/notification/infrastructure/NotificationEntity.java#L18)：首次出现在第 18 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/infrastructure/PointsLedgerEntity.java`](../../backend/src/main/java/com/example/minicommerce/notification/infrastructure/PointsLedgerEntity.java#L18)：首次出现在第 18 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/IdempotencyRecordEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/IdempotencyRecordEntity.java#L18)：首次出现在第 18 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java#L17)：首次出现在第 17 行
- 其余 5 个文件可在 IDE 中全局搜索 `@Table`

## `@Test`

出现 40 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java`](../../backend/src/test/java/com/example/minicommerce/BusinessSafetyIT.java#L88)：首次出现在第 88 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/InfrastructureReadinessTest.java`](../../backend/src/test/java/com/example/minicommerce/InfrastructureReadinessTest.java#L41)：首次出现在第 41 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/LearningReadinessIT.java`](../../backend/src/test/java/com/example/minicommerce/LearningReadinessIT.java#L83)：首次出现在第 83 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/inventory/InventoryConcurrencyIT.java`](../../backend/src/test/java/com/example/minicommerce/inventory/InventoryConcurrencyIT.java#L31)：首次出现在第 31 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/order/CreateOrderIT.java`](../../backend/src/test/java/com/example/minicommerce/order/CreateOrderIT.java#L64)：首次出现在第 64 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/order/domain/OrderEntityTest.java`](../../backend/src/test/java/com/example/minicommerce/order/domain/OrderEntityTest.java#L36)：首次出现在第 36 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/payment/WebhookSignatureTest.java`](../../backend/src/test/java/com/example/minicommerce/payment/WebhookSignatureTest.java#L22)：首次出现在第 22 行
- [`mini-commerce/backend/src/test/java/com/example/minicommerce/shared/domain/MoneyTest.java`](../../backend/src/test/java/com/example/minicommerce/shared/domain/MoneyTest.java#L19)：首次出现在第 19 行

## `@Testcontainers`

出现 1 次。

- [`mini-commerce/backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java`](../../backend/src/test/java/com/example/minicommerce/support/AbstractPostgresIT.java#L29)：首次出现在第 29 行

## `@Transactional`

出现 43 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/application/CartService.java`](../../backend/src/main/java/com/example/minicommerce/cart/application/CartService.java#L45)：首次出现在第 45 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/application/ProductCacheInvalidationConsumer.java`](../../backend/src/main/java/com/example/minicommerce/catalog/application/ProductCacheInvalidationConsumer.java#L34)：首次出现在第 34 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/application/ProductService.java`](../../backend/src/main/java/com/example/minicommerce/catalog/application/ProductService.java#L58)：首次出现在第 58 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/application/AuthService.java`](../../backend/src/main/java/com/example/minicommerce/identity/application/AuthService.java#L51)：首次出现在第 51 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/application/DemoDataInitializer.java`](../../backend/src/main/java/com/example/minicommerce/identity/application/DemoDataInitializer.java#L50)：首次出现在第 50 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/application/InventoryService.java`](../../backend/src/main/java/com/example/minicommerce/inventory/application/InventoryService.java#L23)：首次出现在第 23 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/OrderLifecycleConsumer.java`](../../backend/src/main/java/com/example/minicommerce/messaging/application/OrderLifecycleConsumer.java#L31)：首次出现在第 31 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/application/ProcessedMessageService.java`](../../backend/src/main/java/com/example/minicommerce/messaging/application/ProcessedMessageService.java#L22)：首次出现在第 22 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxJdbcRepository.java`](../../backend/src/main/java/com/example/minicommerce/messaging/infrastructure/OutboxJdbcRepository.java#L23)：首次出现在第 23 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/application/NotificationQueryService.java`](../../backend/src/main/java/com/example/minicommerce/notification/application/NotificationQueryService.java#L24)：首次出现在第 24 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/application/OrderPaidConsumers.java`](../../backend/src/main/java/com/example/minicommerce/notification/application/OrderPaidConsumers.java#L58)：首次出现在第 58 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java`](../../backend/src/main/java/com/example/minicommerce/order/application/CreateOrderService.java#L111)：首次出现在第 111 行
- 其余 5 个文件可在 IDE 中全局搜索 `@Transactional`

## `@UniqueConstraint`

出现 9 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java`](../../backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartEntity.java#L20)：首次出现在第 20 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java`](../../backend/src/main/java/com/example/minicommerce/cart/infrastructure/CartItemEntity.java#L33)：首次出现在第 33 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java`](../../backend/src/main/java/com/example/minicommerce/identity/infrastructure/UserEntity.java#L14)：首次出现在第 14 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/notification/infrastructure/PointsLedgerEntity.java`](../../backend/src/main/java/com/example/minicommerce/notification/infrastructure/PointsLedgerEntity.java#L21)：首次出现在第 21 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/IdempotencyRecordEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/IdempotencyRecordEntity.java#L21)：首次出现在第 21 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderItemEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderItemEntity.java#L17)：首次出现在第 17 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptEntity.java`](../../backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptEntity.java#L23)：首次出现在第 23 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponEntity.java`](../../backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponEntity.java#L21)：首次出现在第 21 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/refund/infrastructure/RefundEntity.java`](../../backend/src/main/java/com/example/minicommerce/refund/infrastructure/RefundEntity.java#L22)：首次出现在第 22 行

## `@Valid`

出现 11 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/cart/api/CartController.java`](../../backend/src/main/java/com/example/minicommerce/cart/api/CartController.java#L38)：首次出现在第 38 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java`](../../backend/src/main/java/com/example/minicommerce/catalog/api/ProductController.java#L58)：首次出现在第 58 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java`](../../backend/src/main/java/com/example/minicommerce/identity/api/AuthController.java#L26)：首次出现在第 26 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java`](../../backend/src/main/java/com/example/minicommerce/inventory/api/InventoryController.java#L37)：首次出现在第 37 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderController.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderController.java#L72)：首次出现在第 72 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java`](../../backend/src/main/java/com/example/minicommerce/order/api/OrderDtos.java#L23)：首次出现在第 23 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java`](../../backend/src/main/java/com/example/minicommerce/payment/api/PaymentController.java#L43)：首次出现在第 43 行

## `@Version`

出现 5 次。

- [`mini-commerce/backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java`](../../backend/src/main/java/com/example/minicommerce/catalog/infrastructure/ProductEntity.java#L50)：首次出现在第 50 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryEntity.java`](../../backend/src/main/java/com/example/minicommerce/inventory/infrastructure/InventoryEntity.java#L29)：首次出现在第 29 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java`](../../backend/src/main/java/com/example/minicommerce/order/infrastructure/OrderEntity.java#L64)：首次出现在第 64 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptEntity.java`](../../backend/src/main/java/com/example/minicommerce/payment/infrastructure/PaymentAttemptEntity.java#L67)：首次出现在第 67 行
- [`mini-commerce/backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponEntity.java`](../../backend/src/main/java/com/example/minicommerce/promotion/infrastructure/UserCouponEntity.java#L42)：首次出现在第 42 行
