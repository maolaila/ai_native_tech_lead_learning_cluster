package com.example.minicommerce.catalog.api;

import static com.example.minicommerce.catalog.api.ProductDtos.CreateProductRequest;
import static com.example.minicommerce.catalog.api.ProductDtos.ProductResponse;
import static com.example.minicommerce.catalog.api.ProductDtos.UpdateProductRequest;

import com.example.minicommerce.catalog.application.ProductService;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/**
 * 商品目录模块的 HTTP/API 适配层。
 *
 * <p><strong>作用：</strong>接收商品查询和管理请求，触发 DTO 校验，并把调用转交给 {@link ProductService}。Controller 不直接访问
 * Repository，也不决定缓存或上下架规则。
 *
 * <p><strong>为什么这样分层：</strong>HTTP 路由、分页参数和状态码属于传输层；商品可售性、缓存失效和审计属于应用用例。 把两者分开后，业务可以脱离 Web
 * 容器测试，也不会因接口形式变化而污染持久化代码。
 *
 * <p><strong>对应文档：</strong> {@code 02_backend_spring/02_Controller_Service_Repository分层.md}、 {@code
 * 02_backend_spring/04_API设计_校验_异常与错误码.md}、 {@code 06_redis/02_CacheAside_TTL与失效.md}。
 */
@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService service;

    public ProductController(ProductService service) {
        this.service = service;
    }

    /** 查询公开商品列表。分页和排序由 API 层定义默认值，真正的“只返回可公开商品”规则由应用服务执行。 */
    @GetMapping
    public Page<ProductResponse> list(
            @PageableDefault(size = 20, sort = "createdAt", direction = Sort.Direction.DESC)
                    Pageable pageable) {
        return service.listPublic(pageable);
    }

    @GetMapping("/{id}")
    public ProductResponse get(@PathVariable Long id) {
        return service.getPublic(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ProductResponse create(@Valid @RequestBody CreateProductRequest request) {
        return service.create(request);
    }

    @PutMapping("/{id}")
    public ProductResponse update(
            @PathVariable Long id, @Valid @RequestBody UpdateProductRequest request) {
        return service.update(id, request);
    }

    /** 使用动作型端点表达“发布商品”，避免允许客户端任意修改状态字段。 */
    @PostMapping("/{id}/publication")
    public ProductResponse publish(@PathVariable Long id) {
        return service.publish(id);
    }
}
