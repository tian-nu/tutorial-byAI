# 116-Mockito与测试替身

> 💡 你要测试 `OrderService`，但它依赖 `PaymentGateway`（调用外部银行接口），还依赖 `InventoryService`（查库存数据库）。你不能每次测试都真的去扣银行卡、减库存。Mockito 让你创建这些依赖的"替身演员"——外貌（接口）一样，但行为完全由你控制。你让它说"支付成功"就成功，说"库存不足"就不足，不涉及任何真实外部资源。

---

## 本章目标
- 理解测试替身的类型：Mock、Stub、Spy
- 使用 Mockito 创建 Mock 对象
- 使用 `when().thenReturn()` 预设行为
- 使用 `verify()` 验证方法调用
- 配合 JUnit 5 的 `@ExtendWith(MockitoExtension.class)`

---

## 116.1 为什么需要 Mock

```java
// OrderService 依赖两个外部服务
@Service
public class OrderService {

    private final PaymentGateway paymentGateway;
    private final InventoryService inventoryService;

    public OrderService(PaymentGateway paymentGateway,
                        InventoryService inventoryService) {
        this.paymentGateway = paymentGateway;
        this.inventoryService = inventoryService;
    }

    public OrderResult placeOrder(Order order) {
        if (!inventoryService.hasStock(order.getProductId(), order.getQuantity())) {
            return OrderResult.outOfStock();
        }
        PaymentResult payment = paymentGateway.pay(order.getAmount());
        if (!payment.isSuccess()) {
            return OrderResult.paymentFailed();
        }
        inventoryService.deduct(order.getProductId(), order.getQuantity());
        return OrderResult.success();
    }
}
```

真实测试时的问题：
- `PaymentGateway` 会真的调用银行 API
- `InventoryService` 需要连接真实数据库
- 测试结果不稳定（网络、余额、库存会变）

---

## 116.2 Mockito 核心三步

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private PaymentGateway paymentGateway;

    @Mock
    private InventoryService inventoryService;

    @Test
    void testPlaceOrderSuccess() {
        // 1. 创建被测对象，注入 mock
        OrderService orderService = new OrderService(paymentGateway, inventoryService);

        // 2. 预设 mock 的行为
        when(inventoryService.hasStock("P001", 2)).thenReturn(true);
        when(paymentGateway.pay(100.0))
                .thenReturn(new PaymentResult(true, "txn-123"));

        // 3. 执行被测方法
        OrderResult result = orderService.placeOrder(
                new Order("P001", 2, 100.0));

        // 4. 断言
        assertEquals("success", result.getStatus());

        // 5. 验证 mock 的方法被调用了
        verify(inventoryService).hasStock("P001", 2);
        verify(paymentGateway).pay(100.0);
        verify(inventoryService).deduct("P001", 2);
    }
}
```

---

## 116.3 预设行为：when().thenXxx()

```java
// 返回值
when(mock.method()).thenReturn(value);
when(mock.method()).thenReturn(value1, value2, value3);  // 第一次返回 value1，第二次 value2...

// 抛异常
when(mock.method()).thenThrow(new RuntimeException("error"));
doThrow(new RuntimeException()).when(mock).voidMethod();  // void 方法

// 真实调用（spy 时用）
when(mock.method()).thenCallRealMethod();

// 自定义答案
when(mock.method()).thenAnswer(invocation -> {
    Object arg = invocation.getArgument(0);
    return "processed: " + arg;
});

// 参数匹配器
when(mock.method(anyString())).thenReturn("default");
when(mock.method(eq("admin"), anyInt())).thenReturn("admin result");
```

### Mock void 方法

```java
// void 方法的 when 写法不同
doNothing().when(mock).voidMethod();

doThrow(new RuntimeException())
    .when(mock).voidMethod();

doAnswer(invocation -> {
    System.out.println("void method called");
    return null;
}).when(mock).voidMethod();
```

---

## 116.4 验证调用：verify()

```java
// 验证调用了
verify(mock).method();

// 验证调用次数
verify(mock, times(1)).method();
verify(mock, times(3)).method();
verify(mock, atLeastOnce()).method();
verify(mock, atLeast(2)).method();
verify(mock, atMost(5)).method();
verify(mock, never()).method();

// 验证调用顺序
InOrder inOrder = inOrder(mock1, mock2);
inOrder.verify(mock1).firstMethod();
inOrder.verify(mock2).secondMethod();

// 验证之后不再有交互
verifyNoMoreInteractions(mock);
```

---

## 116.5 Spy——部分 Mock

Spy 是"真的对象，但我可以篡改它的部分行为"。

```java
@Test
void testSpy() {
    List<String> spyList = spy(new ArrayList<>());

    // 真实调用
    spyList.add("one");
    assertEquals(1, spyList.size());

    // 篡改 size() 的行为
    when(spyList.size()).thenReturn(100);
    assertEquals(100, spyList.size());
}
```

### Spy vs Mock

| | Mock | Spy |
|------|------|-----|
| 默认行为 | 所有方法返回默认值 | 调用真实方法 |
| 使用 | `mock(Class.class)` | `spy(new Object())` |
| 适用场景 | 完全隔离外部依赖 | 部分方法需要真实逻辑 |

> ⚠️ Spy 慎用 `when(spy.method())`：`when()` 会先真实调用一次 `method()`。用 `doReturn().when(spy).method()` 替代。

---

## 116.6 @InjectMocks——自动注入 Mock

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private PaymentGateway paymentGateway;

    @Mock
    private InventoryService inventoryService;

    @InjectMocks
    private OrderService orderService;  // Mockito 自动把 @Mock 注入进来

    @Test
    void testPlaceOrder() {
        // 不需要 new OrderService(...)
        when(inventoryService.hasStock(anyString(), anyInt())).thenReturn(true);
        // ...
    }
}
```

### @InjectMocks 的限制

- 只支持构造器注入和 setter 注入
- 如果字段名和 Mock 名不匹配，可能需要手动关联
- 复杂场景下，手动 `new` 并传参更显式、更安全

---

## 116.7 ArgumentCaptor——捕获方法参数

当你想检查传给 mock 的参数内容时：

```java
@Test
void testArgumentCapture() {
    ArgumentCaptor<Order> captor = ArgumentCaptor.forClass(Order.class);

    orderService.placeOrder(new Order("P001", 2, 100.0));

    verify(inventoryService).deduct(anyString(), anyInt());
    // 如果 deduct 的参数是一个对象：
    // verify(inventoryService).save(captor.capture());
    // Order captured = captor.getValue();
    // assertEquals("P001", captured.getProductId());
}
```

---

## 116.8 Boilerplate 对比：手工 Stub vs Mockito

```java
// ❌ 手工 Stub：每一个方法都要写匿名类
PaymentGateway stub = new PaymentGateway() {
    @Override
    public PaymentResult pay(Double amount) {
        return new PaymentResult(true, "txn-123");
    }
    @Override
    public PaymentResult refund(String txnId) {
        return new PaymentResult(true, "ref-456");
    }
};

// ✅ Mockito：一行搞定
PaymentGateway mock = mock(PaymentGateway.class);
when(mock.pay(100.0)).thenReturn(new PaymentResult(true, "txn-123"));
```

---

## 116.9 完成效果

学完本章，你应该能：
1. 用 Mockito 隔离外部依赖，编写纯单元测试
2. 用 `when().thenReturn()` 控制 Mock 行为
3. 用 `verify()` 验证方法是否被正确调用
4. 区分 Mock、Spy、Stub 的使用场景

---

## 小结

| 知识点 | 核心 API |
|--------|----------|
| 创建 Mock | `@Mock` + `@ExtendWith(MockitoExtension.class)` |
| 自动注入 | `@InjectMocks` |
| 预设行为 | `when(mock.method()).thenReturn(value)` |
| 预设异常 | `when(mock.method()).thenThrow(ex)` / `doThrow().when(mock).voidMethod()` |
| 验证调用 | `verify(mock).method()` / `verify(mock, times(n))` |
| Spy | `spy(realObject)` + `doReturn().when(spy)` |
| 参数捕获 | `ArgumentCaptor.forClass()` |

---

## 自测题

1. `@Mock` 和 `@Spy` 的核心区别是什么？
2. 你有一个 void 方法 `emailService.send(Email email)`，想测试它被调用了一次且参数正确。怎么写？
3. 为什么 Spy 不推荐用 `when(spy.method())`？

<details>
<summary>点击查看答案</summary>

1. `@Mock` 创建的对象所有方法都返回默认值（null/0/false），完全不执行真实逻辑；`@Spy` 创建的对象默认调用真实方法，只有被 `when` 覆盖的方法才返回预设值。
2. 
```java
verify(emailService, times(1)).send(emailCaptor.capture());
Email captured = emailCaptor.getValue();
assertEquals("user@example.com", captured.getTo());
```
3. `when(spy.method())` 在执行 `when()` 时就会真实调用一次 `method()`，可能导致副作用。正确写法：`doReturn(value).when(spy).method()` 不会真实调用。
</details>