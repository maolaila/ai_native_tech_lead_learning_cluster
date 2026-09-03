package com.example.minicommerce.messaging.config;
import org.springframework.amqp.core.*;import org.springframework.amqp.rabbit.core.RabbitTemplate;import org.springframework.context.annotation.*;
/** 对应文档：07_rabbitmq/02_Exchange_Queue_Routing.md、07_rabbitmq/03_Confirm_Ack_Retry_DLQ.md。 */
@Configuration public class RabbitTopology{
 public static final String EVENTS="commerce.events";public static final String DLX="commerce.dlx";public static final String NOTIFICATION_Q="notification.order-paid.v1";public static final String POINTS_Q="points.order-paid.v1";public static final String CACHE_Q="cache.product-changed.v1";
 @Bean TopicExchange commerceExchange(){return new TopicExchange(EVENTS,true,false);}@Bean DirectExchange deadLetterExchange(){return new DirectExchange(DLX,true,false);}
 private Queue durable(String name){return QueueBuilder.durable(name).deadLetterExchange(DLX).deadLetterRoutingKey(name+".dead").build();}
 @Bean Queue notificationQueue(){return durable(NOTIFICATION_Q);}@Bean Queue pointsQueue(){return durable(POINTS_Q);}@Bean Queue cacheQueue(){return durable(CACHE_Q);}
 @Bean Queue notificationDlq(){return QueueBuilder.durable(NOTIFICATION_Q+".dlq").build();}@Bean Queue pointsDlq(){return QueueBuilder.durable(POINTS_Q+".dlq").build();}@Bean Queue cacheDlq(){return QueueBuilder.durable(CACHE_Q+".dlq").build();}
 @Bean Binding notificationBinding(Queue notificationQueue,TopicExchange commerceExchange){return BindingBuilder.bind(notificationQueue).to(commerceExchange).with("order.paid.v1");}
 @Bean Binding pointsBinding(Queue pointsQueue,TopicExchange commerceExchange){return BindingBuilder.bind(pointsQueue).to(commerceExchange).with("order.paid.v1");}
 @Bean Binding cacheBinding(Queue cacheQueue,TopicExchange commerceExchange){return BindingBuilder.bind(cacheQueue).to(commerceExchange).with("product.changed.v1");}
 @Bean Binding notificationDead(Queue notificationDlq,DirectExchange deadLetterExchange){return BindingBuilder.bind(notificationDlq).to(deadLetterExchange).with(NOTIFICATION_Q+".dead");}
 @Bean Binding pointsDead(Queue pointsDlq,DirectExchange deadLetterExchange){return BindingBuilder.bind(pointsDlq).to(deadLetterExchange).with(POINTS_Q+".dead");}
 @Bean Binding cacheDead(Queue cacheDlq,DirectExchange deadLetterExchange){return BindingBuilder.bind(cacheDlq).to(deadLetterExchange).with(CACHE_Q+".dead");}
 @Bean RabbitTemplateCustomizer mandatoryReturns(){return template->template.setMandatory(true);}public interface RabbitTemplateCustomizer{void customize(RabbitTemplate template);}
 @Bean org.springframework.boot.ApplicationRunner customizeRabbit(RabbitTemplate template,RabbitTemplateCustomizer customizer){return args->customizer.customize(template);}
}
