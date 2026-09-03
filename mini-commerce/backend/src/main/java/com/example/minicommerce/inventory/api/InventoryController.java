package com.example.minicommerce.inventory.api;

import com.example.minicommerce.inventory.application.InventoryService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.PositiveOrZero;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController @RequestMapping("/api/inventory")
public class InventoryController{
 private final InventoryService service; public InventoryController(InventoryService service){this.service=service;}
 @GetMapping("/{productId}") @PreAuthorize("hasAnyRole('ADMIN','SUPPORT')")
 InventoryService.InventoryView get(@PathVariable Long productId){return service.get(productId);}
 @PutMapping("/{productId}") @PreAuthorize("hasRole('ADMIN')")
 InventoryService.InventoryView replace(@PathVariable Long productId,@Valid @RequestBody ReplaceRequest r){return service.replaceAvailable(productId,r.available());}
 public record ReplaceRequest(@PositiveOrZero int available){}
}
