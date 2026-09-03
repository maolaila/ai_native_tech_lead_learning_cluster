package com.example.minicommerce.catalog.api;

import static com.example.minicommerce.catalog.api.ProductDtos.*;
import com.example.minicommerce.catalog.application.ProductService;
import jakarta.validation.Valid;
import org.springframework.data.domain.*;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

/** 对应文档：02_backend_spring/02_Controller_Service_Repository分层.md。Controller 不直接访问 Repository。 */
@RestController
@RequestMapping("/api/products")
public class ProductController {
    private final ProductService service;
    public ProductController(ProductService service){this.service=service;}
    @GetMapping public Page<ProductResponse> list(@PageableDefault(size=20,sort="createdAt",direction=Sort.Direction.DESC) Pageable p){return service.listPublic(p);}
    @GetMapping("/{id}") public ProductResponse get(@PathVariable Long id){return service.getPublic(id);}
    @PostMapping @ResponseStatus(HttpStatus.CREATED) public ProductResponse create(@Valid @RequestBody CreateProductRequest r){return service.create(r);}
    @PutMapping("/{id}") public ProductResponse update(@PathVariable Long id,@Valid @RequestBody UpdateProductRequest r){return service.update(id,r);}
    @PostMapping("/{id}/publication") public ProductResponse publish(@PathVariable Long id){return service.publish(id);}
}
