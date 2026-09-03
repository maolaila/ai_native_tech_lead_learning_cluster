package com.example.minicommerce.messaging.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.QueueBuilder;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * RabbitMQ 的 Exchange、Queue、Binding 和死信队列配置。
 *
 * <p><strong>大白话：</strong>Producer 先把消息交给 Exchange；Exchange 根据 Routing Key 和 Binding 规则，把消息放进一个或多个 Queue；
 * Consumer 再从各自 Queue 读取。
 *
 * <p><strong>为什么通知和积分使用两个 Queue：</strong>同一个“订单已支付”事件需要让通知和积分都处理。
 * 两个独立 Queue 会各保存一份消息；如果只是同一个 Queue 配两个 Consumer，它们会竞争消息，通常只有一个拿到。
 *
 * <p><strong>对应文档：</strong> {@code 07_rabbitmq/02_Exchange_Queue_Routing.md}、 {@code
 * 07_rabbitmq/03_Confirm_Ack_Retry_DLQ.md}、 {@code mini-commerce/docs/BACKEND-TERMS-PLAIN-CHINESE.md}。
 */
// @Configuration：这个类集中声明 RabbitMQ 需要的基础对象。
@Configuration
public class RabbitTopology {
    public static final String EVENTS = "commerce.events";
    public static final String DLX = "commerce.dlx";
    public static final String NOTIFICATION_Q = "notification.order-paid.v1";
    public static final String POINTS_Q = "points.order-paid.v1";
    public static final String CACHE_Q = "cache.product-changed.v1";

    /** Topic Exchange 可以根据带点号的 Routing Key 模式分发业务事件。 */
    @Bean
    TopicExchange commerceExchange() {
        // durable=true：RabbitMQ 重启后仍保留；autoDelete=false：没有消费者时也不自动删除。
        return new TopicExchange(EVENTS, true, false);
    }

    /** 失败消息进入死信 Exchange，再按精确 Routing Key 分发到对应 DLQ。 */
    @Bean
    DirectExchange deadLetterExchange() {
        return new DirectExchange(DLX, true, false);
    }

    /** 创建一个持久化业务队列，并指定处理失败后的死信去向。 */
    private Queue durable(String name) {
        return QueueBuilder.durable(name)
                .deadLetterExchange(DLX)
                .deadLetterRoutingKey(name + ".dead")
                .build();
    }

    // 每个 @Bean 方法返回的对象都会交给 Spring 管理，并由 Spring AMQP 声明到 RabbitMQ。
    @Bean
    Queue notificationQueue() {
        return durable(NOTIFICATION_Q);
    }

    @Bean
    Queue pointsQueue() {
        return durable(POINTS_Q);
    }

    @Bean
    Queue cacheQueue() {
        return durable(CACHE_Q);
    }

    /** 通知消息多次失败后进入这里，避免坏消息无限阻塞正常队列。 */
    @Bean
    Queue notificationDlq() {
        return QueueBuilder.durable(NOTIFICATION_Q + ".dlq").build();
    }

    @Bean
    Queue pointsDlq() {
        return QueueBuilder.durable(POINTS_Q + ".dlq").build();
    }

    @Bean
    Queue cacheDlq() {
        return QueueBuilder.durable(CACHE_Q + ".dlq").build();
    }

    /** order.paid.v1 同时路由到通知队列。 */
    @Bean
    Binding notificationBinding(
            Queue notificationQueue, TopicExchange commerceExchange) {
        return BindingBuilder.bind(notificationQueue)
                .to(commerceExchange)
                .with("order.paid.v1");
    }

    /** order.paid.v1 也路由到积分队列，所以通知和积分都会收到。 */
    @Bean
    Binding pointsBinding(Queue pointsQueue, TopicExchange commerceExchange) {
        return BindingBuilder.bind(pointsQueue)
                .to(commerceExchange)
                .with("order.paid.v1");
    }

    /** 商品变化事件只路由到缓存失效队列。 */
    @Bean
    Binding cacheBinding(Queue cacheQueue, TopicExchange commerceExchange) {
        return BindingBuilder.bind(cacheQueue)
                .to(commerceExchange)
                .with("product.changed.v1");
    }

    @Bean
    Binding notificationDead(
            Queue notificationDlq, DirectExchange deadLetterExchange) {
        return BindingBuilder.bind(notificationDlq)
                .to(deadLetterExchange)
                .with(NOTIFICATION_Q + ".dead");
    }

    @Bean
    Binding pointsDead(Queue pointsDlq, DirectExchange deadLetterExchange) {
        return BindingBuilder.bind(pointsDlq)
                .to(deadLetterExchange)
                .with(POINTS_Q + ".dead");
    }

    @Bean
    Binding cacheDead(Queue cacheDlq, DirectExchange deadLetterExchange) {
        return BindingBuilder.bind(cacheDlq)
                .to(deadLetterExchange)
                .with(CACHE_Q + ".dead");
    }

    /**
     * mandatory=true：如果消息无法路由到任何 Queue，RabbitMQ 会把它退回给发送方，而不是悄悄丢弃。
     */
    @Bean
    RabbitTemplateCustomizer mandatoryReturns() {
        return template -> template.setMandatory(true);
    }

    /** 一个很小的配置接口，让 RabbitTemplate 的额外设置可以独立测试和替换。 */
    public interface RabbitTemplateCustomizer {
        void customize(RabbitTemplate template);
    }

    /** 应用启动后执行一次 RabbitTemplate 自定义配置。 */
    @Bean
    org.springframework.boot.ApplicationRunner customizeRabbit(
            RabbitTemplate template, RabbitTemplateCustomizer customizer) {
        return args -> customizer.customize(template);
    }
}
