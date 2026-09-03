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
 * 订单模块的 HTTP/API 适配层。
 *
 * <p><strong>作用：</strong>取得认证用户、请求体、路径参数和 {@code Idempotency-Key}，然后调用订单应用服务。
 * Controller 不计算金额、不扣库存，也不直接修改订单状态。</p>
 *
 * <p><strong>为什么拆成 Create、Command、Query 三个应用服务：</strong>创建订单具有较大的事务和幂等边界；
 * 取消等命令负责状态变化；查询只负责读取和对象级权限。分开后，每种用例的职责、事务和测试目标都更清楚。</p>
 *
 * <p><strong>对应文档：</strong>
 * {@code 02_backend_spring/02_Controller_Service_Repository分层.md}、
 * {@code 02_backend_spring/04_API设计_校验_异常与错误码.md}、
 * {@code 02_backend_spring/06_订单模块案例.md}、
 * {@code 05_auth_security/02_RBAC与对象级权限.md}。</p>
 */
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    private final CreateOrderService createOrderService;
    private final OrderCommandService commandService;
    private final OrderQueryService queryService;
    private final CurrentUser currentUser;

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
     * <p>网络超时不能证明服务端没有成功，因此写请求要求客户端提供幂等键；真正的请求指纹、并发竞争和结果复用在应用层处理。</p>
     */
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public OrderResponse create(
            @RequestHeader("Idempotency-Key") String idempotencyKey,
            @Valid @RequestBody CreateOrderRequest request) {
        return createOrderService.create(currentUser.require().id(), idempotencyKey, request);
    }

    /** 查询订单时，应用层还会验证该订单是否属于当前用户或当前角色是否拥有跨用户读取权限。 */
    @GetMapping("/{id}")
    public OrderResponse get(@PathVariable UUID id) {
        return queryService.get(id, currentUser.require());
    }

    @GetMapping
    public Page<OrderResponse> list(
            @PageableDefault(
                            size = 20,
                            sort = "createdAt",
                            direction = Sort.Direction.DESC)
                    Pageable pageable) {
        return queryService.list(currentUser.require(), pageable);
    }

    /** 使用明确的取消动作，而不是开放 {@code PATCH status=CANCELLED} 让客户端任意设置状态。 */
    @PostMapping("/{id}/cancellation")
    public OrderResponse cancel(@PathVariable UUID id) {
        return commandService.cancel(id, currentUser.require());
    }
}
