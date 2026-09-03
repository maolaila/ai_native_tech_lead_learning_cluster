package com.example.minicommerce.identity.api;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public final class AuthDtos {
    private AuthDtos() {}
    public record RegisterRequest(@Email @NotBlank String email, @NotBlank @Size(max = 100) String displayName,
                                  @NotBlank @Size(min = 10, max = 100) String password) {}
    public record LoginRequest(@Email @NotBlank String email, @NotBlank String password) {}
    public record RefreshRequest(@NotBlank String refreshToken) {}
    public record LogoutRequest(@NotBlank String refreshToken) {}
    public record TokenResponse(String accessToken, String refreshToken, long expiresInSeconds,
                                Long userId, String email, String role) {}
}
