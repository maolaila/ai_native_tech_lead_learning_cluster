package com.example.minicommerce.order.api;

import static com.example.minicommerce.order.api.OrderDtos.CreateOrderRequest;
import static com.example.minicommerce.order.api.OrderDtos.OrderResponse;

import com.example.minicommerce.order.application.CreateOrderService;
import com.example.minicommerce.order.application.OrderCommandService;
import com.example.minicommerce.order.application.OrderQueryService;
import com.example.minicommerce.shared.security.CurrentUser;
import jakarta.validation.Valid;
import java.util.UUID;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/**
 * 订单模块的 HTTP 请求入口。
 *
 * <p><strong>作用：</strong>取得当前用户、请求体、URL 参数和 {@code Idempotency-Key}，再把任务交给订单应用服务。 Controller
 * 不计算金额、不扣库存，也不直接访问 Repository。
 *
 * <p><strong>大白话：</strong>Controller 是门口接待。它负责把 HTTP 请求整理好，再交给真正的业务负责人处理。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/02_Controller_Service_Repository分层.md}、 {@code
 * 02_backend_spring/04_API设计_校验_异常与错误码.md}、 {@code 02_backend_spring/06_订单模块案例.md}、 {@code
 * mini-commerce/docs/REQUEST-TO-DATABASE-WALKTHROUGH.md}。
 */
// @RestController：这个类接收 HTTP 请求，方法返回值通常自动转换成 JSON。
@RestController
// 本类接口共同使用 /api/orders 作为 URL 开头。
@RequestMapping("/api/orders")
public class OrderController {
    private final CreateOrderService createOrderService;
    private final OrderCommandService commandService;
    private final OrderQueryService queryService;
    private final CurrentUser currentUser;

    /** Spring 通过构造器把所需服务传进来，这叫构造器注入。 */
    public OrderController(
            CreateOrderService createOrderService,
            OrderCommandService commandService,
            OrderQueryService queryService,
            CurrentUser currentUser) {
        this.createOrderService = createOrderService;
        this.commandService = commandService;
        this.queryService = queryService;
        this.currentUser = currentUser;
    }

    /**
     * 创建订单。
     *
     * <p>网络超时后客户端可能重试，所以创建订单要求幂等键。请求指纹、并发竞争和原结果复用在 {@link CreateOrderService} 中处理。
     */
    // @PostMapping：处理 POST /api/orders。
    @PostMapping
    // 创建成功返回 201 Created。
    @ResponseStatus(HttpStatus.CREATED)
    public OrderResponse create(
            // @RequestHeader：从 HTTP 请求头读取 Idempotency-Key。
            @RequestHeader("Idempotency-Key") String idempotencyKey,
            // @RequestBody 把 JSON 转成 Java DTO；@Valid 先执行基础字段校验。
            @Valid @RequestBody CreateOrderRequest request) {
        return createOrderService.create(currentUser.require().id(), idempotencyKey, request);
    }

    /** 查询一张订单；应用层还会检查该订单是否属于当前用户。 */
    @GetMapping("/{id}")
    public OrderResponse get(
            // @PathVariable：从 /api/orders/{id} 的 URL 路径中取出订单 ID。
            @PathVariable UUID id) {
        return queryService.get(id, currentUser.require());
    }

    /** 分页查询当前用户有权看到的订单。 */
    @GetMapping
    public Page<OrderResponse> list(
            // 没传分页参数时，默认每页 20 条并按 createdAt 倒序。
            @PageableDefault(size = 20, sort = "createdAt", direction = Sort.Direction.DESC)
                    Pageable pageable) {
        return queryService.list(currentUser.require(), pageable);
    }

    /** 使用明确的取消动作，而不是开放任意修改 status 字段。 */
    @PostMapping("/{id}/cancellation")
    public OrderResponse cancel(@PathVariable UUID id) {
        return commandService.cancel(id, currentUser.require());
    }
}
