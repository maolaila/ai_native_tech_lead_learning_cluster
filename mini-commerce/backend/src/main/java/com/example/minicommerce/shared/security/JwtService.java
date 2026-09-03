package com.example.minicommerce.shared.security;

import com.example.minicommerce.identity.infrastructure.UserEntity;
import com.example.minicommerce.shared.config.AppProperties;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import java.time.Clock;
import java.time.Instant;
import java.util.Date;
import javax.crypto.SecretKey;
import org.springframework.stereotype.Service;

/**
 * 短期 Access Token 只承载身份和角色，不放密码、私密资料或可长期依赖的业务状态。
 * 对应文档：05_auth_security/01_Session_Cookie_Token.md。
 */
@Service
public class JwtService {
    private final AppProperties properties;
    private final Clock clock;
    private final SecretKey key;

    public JwtService(AppProperties properties, Clock clock) {
        this.properties = properties;
        this.clock = clock;
        this.key = Keys.hmacShaKeyFor(Decoders.BASE64.decode(properties.jwt().secret()));
    }

    public String issue(UserEntity user) {
        Instant now = clock.instant();
        return Jwts.builder()
            .issuer(properties.jwt().issuer())
            .subject(user.getEmail())
            .claim("uid", user.getId())
            .claim("role", user.getRole().name())
            .issuedAt(Date.from(now))
            .expiration(Date.from(now.plus(properties.jwt().accessTtl())))
            .signWith(key)
            .compact();
    }

    public Claims parse(String token) {
        return Jwts.parser().requireIssuer(properties.jwt().issuer()).verifyWith(key).build()
            .parseSignedClaims(token).getPayload();
    }
}
