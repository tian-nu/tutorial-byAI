# 第107章 · Mock与测试替身

> "你的Service层依赖Repository层，Repository层依赖数据库。你要测Service层——总不能每次都启动一个MySQL吧？你要测支付功能——总不能真的给支付宝打1分钱吧？Mock就是你的'替身演员'：替真实依赖上场，按你的指挥说台词、做动作——目的是让你的被测代码独舞，不受杂音干扰。"

---

## 107.1 什么是Mock

### 类比：驾校训练 vs 真实上路

**上路练车**：真实的道路、真实的车辆、真实的行人。一旦出错就是真事故。这对应**集成测试**——用真实的数据库、真实的第三方API。

**驾校模拟器**：屏幕上的虚拟道路，出错了不会出车祸。可以在各种极端条件（暴雨、爆胎）下练习，而这些条件在真实道路上很难复现。这对应**Mock**（测试用的替身对象，模拟真实依赖行为并验证调用，详见附录I）——用假的依赖，可以模拟任何场景。

### 什么时候需要Mock

Mock的核心原则：**Mock你依赖的东西，而不是你测的东西。**

```
你要测 UserService.Register()
它依赖:
├── UserRepo（存数据库）     ← Mock这个（不想真的写数据库）
├── EmailService（发激活邮件）  ← Mock这个（不想真的发邮件）
└── PasswordHasher（哈希密码）  ← 可以不Mock（纯CPU计算，快且无副作用）
```

### 测试替身（Test Double，测试中替代真实依赖的模拟对象统称，详见附录I）的五种类型

| 类型 | 相当于 | 用途 |
|------|--------|------|
| **Dummy** | 空壳 | 占位用，实际不用 |
| **Stub** | 提词器 | 返回预设的固定值 |
| **Spy** | 监控探头 | 记录被调用的方式和次数 |
| **Mock** | 替身演员 | 预设行为 + 验证调用 |
| **Fake** | 简易版 | 真实但简化的实现（如SQLite代替MySQL） |

实践中，Go开发者常说的"Mock"实际上涵盖了Stub、Spy和Mock的混合。

---

## 107.2 Go Mock方案：接口+手动Mock

### 为什么Go的Mock靠接口

Go的接口是**隐式实现**的——只要一个类型有接口要求的所有方法，它就"自动"实现了这个接口，不需要显式声明 `implements`。

这意味着：你可以写一个接口，然后为测试专门写一个假实现——被测代码感知不到任何区别。

### 实战：手动Mock

**真实代码结构：**

```go
package user

type UserRepo interface {
    GetByEmail(email string) (*User, error)
    Create(user *User) (int64, error)
}

type EmailService interface {
    SendActivation(email string, token string) error
}

type UserService struct {
    repo  UserRepo
    email EmailService
}

func NewUserService(repo UserRepo, email EmailService) *UserService {
    return &UserService{repo: repo, email: email}
}

func (s *UserService) Register(email, password string) (*User, error) {
    existing, err := s.repo.GetByEmail(email)
    if err != nil {
        return nil, err
    }
    if existing != nil {
        return nil, errors.New("邮箱已被注册")
    }

    user := &User{Email: email, Password: hashPassword(password)}
    id, err := s.repo.Create(user)
    if err != nil {
        return nil, err
    }
    user.ID = id

    token := generateToken()
    _ = s.email.SendActivation(email, token)

    return user, nil
}
```

**Mock实现：**

```go
package user

type MockUserRepo struct {
    GetByEmailFunc func(email string) (*User, error)
    CreateFunc     func(user *User) (int64, error)
}

func (m *MockUserRepo) GetByEmail(email string) (*User, error) {
    return m.GetByEmailFunc(email)
}

func (m *MockUserRepo) Create(user *User) (int64, error) {
    return m.CreateFunc(user)
}

type MockEmailService struct {
    SendActivationFunc func(email, token string) error
}

func (m *MockEmailService) SendActivation(email, token string) error {
    return m.SendActivationFunc(email, token)
}
```

**测试代码：**

```go
func TestUserService_Register_Success(t *testing.T) {
    mockRepo := &MockUserRepo{
        GetByEmailFunc: func(email string) (*User, error) {
            return nil, nil
        },
        CreateFunc: func(user *User) (int64, error) {
            return 1, nil
        },
    }

    mockEmail := &MockEmailService{
        SendActivationFunc: func(email, token string) error {
            assert.Equal(t, "alice@example.com", email)
            assert.NotEmpty(t, token)
            return nil
        },
    }

    service := NewUserService(mockRepo, mockEmail)

    user, err := service.Register("alice@example.com", "password123")

    assert.NoError(t, err)
    assert.NotNil(t, user)
    assert.Equal(t, "alice@example.com", user.Email)
    assert.Equal(t, int64(1), user.ID)
}

func TestUserService_Register_DuplicateEmail(t *testing.T) {
    mockRepo := &MockUserRepo{
        GetByEmailFunc: func(email string) (*User, error) {
            return &User{ID: 1, Email: email}, nil
        },
        CreateFunc: func(user *User) (int64, error) {
            return 0, nil
        },
    }

    mockEmail := &MockEmailService{
        SendActivationFunc: func(email, token string) error {
            return nil
        },
    }

    service := NewUserService(mockRepo, mockEmail)

    user, err := service.Register("alice@example.com", "password123")

    assert.Error(t, err)
    assert.Nil(t, user)
    assert.Contains(t, err.Error(), "已被注册")
}
```

**这种模式的好处：**
- 每个测试用例可以独立设定Mock的行为
- Mock的行为和测试代码在一起，读测试就知道Mock做了什么
- 不需要任何第三方库

---

## 107.3 gomock：官方Mock框架

### 安装

```bash
go install github.com/golang/mock/mockgen@latest
```

### 使用步骤

**Step 1：定义接口（使用 `go:generate` 注释）**

```go
package user

//go:generate mockgen -destination=mocks/mock_userrepo.go -package=mocks . UserRepo
type UserRepo interface {
    GetByEmail(email string) (*User, error)
    Create(user *User) (int64, error)
}
```

**Step 2：生成Mock代码**

```bash
go generate ./...
```

`mockgen` 会根据接口定义自动生成 `mocks/mock_userrepo.go` 文件。

**Step 3：在测试中使用**

```go
func TestWithGoMock(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := mocks.NewMockUserRepo(ctrl)

    mockRepo.EXPECT().
        GetByEmail("alice@example.com").
        Return(nil, nil).
        Times(1)

    mockRepo.EXPECT().
        Create(gomock.Any()).
        Return(int64(1), nil).
        Times(1)

    service := NewUserService(mockRepo, &RealEmailService{})

    user, err := service.Register("alice@example.com", "password123")

    assert.NoError(t, err)
    assert.NotNil(t, user)
}
```

**gomock的EXPECT玩法：**

```go
mock.EXPECT().Method("参数").Return(返回值, 错误).Times(调用次数)

gomock.Any()         // 匹配任意参数
gomock.Eq("hello")   // 精确匹配
gomock.Not(gomock.Eq(""))  // 匹配非空字符串

.Times(1)            // 期望被调用1次
.Times(0)            // 期望不被调用
.AnyTimes()          // 任意次数
.MinTimes(1)         // 至少1次

.Return(...)         // 返回固定值
.DoAndReturn(func(...) { ... })  // 动态返回
.Do(func(...) { ... })           // 只执行副作用
```

### gomock vs 手动Mock

| | 手动Mock | gomock |
|---|---|---|
| **优点** | 无依赖、简单直观、灵活性高 | 自动生成、调用次数验证、类型安全 |
| **缺点** | 手写代码多、容易遗漏接口变更 | 需要安装mockgen、生成的代码不直观 |
| **适合** | 小型项目、简单接口 | 大型项目、接口频繁变更 |

---

## 107.4 数据库测试策略

### 方案对比

| 方案 | 速度 | 真实度 | 复杂度 |
|------|------|--------|--------|
| Mock Repository | 极快 | 低（不真走SQL） | 低 |
| SQLite内存模式 | 快 | 中（走SQL但不是MySQL） | 中 |
| Docker临时MySQL | 慢 | 高（完全真实） | 高 |
| 测试用真实MySQL | 中 | 极高 | 中（需要维护测试数据库） |

### 推荐策略：分层选择

```
Repository层测试 → SQLite内存模式（测SQL是否正确）
Service层测试    → Mock Repository（测业务逻辑是否正确）
集成测试         → Docker临时MySQL（端到端验证）
```

上章的106.7节已经展示了Repository层用SQLite内存模式。本章107.2展示了Service层Mock Repository。

---

## 107.5 实战：Mock数据库层测试Service层

完整展示一个订单Service的测试：

```go
package order

import (
    "testing"
    "errors"

    "github.com/stretchr/testify/assert"
)

type Order struct {
    ID     int64
    UserID int64
    Amount float64
    Status string
}

type OrderRepo interface {
    Create(order *Order) (int64, error)
    GetByID(id int64) (*Order, error)
    UpdateStatus(id int64, status string) error
}

type StockService interface {
    Deduct(productID int64, quantity int) error
}

type OrderService struct {
    repo  OrderRepo
    stock StockService
}

func NewOrderService(repo OrderRepo, stock StockService) *OrderService {
    return &OrderService{repo: repo, stock: stock}
}

func (s *OrderService) PlaceOrder(userID, productID int64, amount float64, quantity int) (*Order, error) {
    if amount <= 0 {
        return nil, errors.New("金额必须大于0")
    }
    if quantity <= 0 {
        return nil, errors.New("数量必须大于0")
    }

    err := s.stock.Deduct(productID, quantity)
    if err != nil {
        return nil, err
    }

    order := &Order{
        UserID: userID,
        Amount: amount,
        Status: "pending",
    }
    id, err := s.repo.Create(order)
    if err != nil {
        return nil, err
    }
    order.ID = id

    return order, nil
}

type MockOrderRepo struct {
    CreateFunc       func(order *Order) (int64, error)
    GetByIDFunc      func(id int64) (*Order, error)
    UpdateStatusFunc func(id int64, status string) error
}

func (m *MockOrderRepo) Create(order *Order) (int64, error) {
    return m.CreateFunc(order)
}

func (m *MockOrderRepo) GetByID(id int64) (*Order, error) {
    return m.GetByIDFunc(id)
}

func (m *MockOrderRepo) UpdateStatus(id int64, status string) error {
    return m.UpdateStatusFunc(id, status)
}

type MockStockService struct {
    DeductFunc func(productID int64, quantity int) error
}

func (m *MockStockService) Deduct(productID int64, quantity int) error {
    return m.DeductFunc(productID, quantity)
}

func TestOrderService_PlaceOrder_Success(t *testing.T) {
    mockRepo := &MockOrderRepo{
        CreateFunc: func(order *Order) (int64, error) {
            assert.Equal(t, "pending", order.Status)
            return 100, nil
        },
    }

    mockStock := &MockStockService{
        DeductFunc: func(productID int64, quantity int) error {
            assert.Equal(t, int64(10), productID)
            assert.Equal(t, 2, quantity)
            return nil
        },
    }

    service := NewOrderService(mockRepo, mockStock)

    order, err := service.PlaceOrder(1, 10, 99.99, 2)

    assert.NoError(t, err)
    assert.NotNil(t, order)
    assert.Equal(t, int64(100), order.ID)
    assert.Equal(t, 99.99, order.Amount)
    assert.Equal(t, "pending", order.Status)
}

func TestOrderService_PlaceOrder_InvalidAmount(t *testing.T) {
    service := NewOrderService(nil, nil)

    order, err := service.PlaceOrder(1, 10, 0, 2)

    assert.Error(t, err)
    assert.Nil(t, order)
    assert.Contains(t, err.Error(), "金额")
}

func TestOrderService_PlaceOrder_StockDeductionFailed(t *testing.T) {
    mockStock := &MockStockService{
        DeductFunc: func(productID int64, quantity int) error {
            return errors.New("库存不足")
        },
    }

    service := NewOrderService(nil, mockStock)

    order, err := service.PlaceOrder(1, 10, 99.99, 2)

    assert.Error(t, err)
    assert.Nil(t, order)
    assert.Contains(t, err.Error(), "库存不足")
}
```

**测试覆盖的场景：**
1. ✅ 正常下单
2. ✅ 金额无效
3. ✅ 库存扣除失败
4. （还可以加：数量无效、创建订单时数据库报错等）

每个场景通过设定Mock的不同行为来模拟真实世界可能发生的各种情况——这就是Mock的威力。

---

## 🤔 想多一点：不要Mock一切

Mock是一个强大的工具，但过度使用会适得其反：

**应该Mock的：**
- 外部网络请求（第三方API、支付网关、短信服务）
- 数据库读写（在测试Service层时）
- 文件系统操作
- 时间相关（让"当前时间"可控）
- 随机数

**不应该Mock的：**
- 简单的纯函数（如 `hashPassword`、`calculateTax`）
- 你拥有的数据结构（如 `User`、`Order`）
- 过于简单的依赖（Mock一个 `strings.ToUpper`？没必要）

**Mock的反模式：**
当你发现自己在Mock一个Mock返回的结果时——停下来。你的设计可能出了问题。好代码的依赖关系应该是：**依赖注入 + 接口隔离 + 职责单一**。如果Mock变得异常复杂，说明被Mock的接口太大了，该拆分了。

---

## 本章小结

| 知识点 | 要点 |
|--------|------|
| Mock | 测试替身，替代真实依赖，模拟各种场景 |
| 什么时候Mock | 外部网络、数据库、文件系统、时间、随机数 |
| Go的Mock基础 | 接口隐式实现 + 手动Mock实现（函数字段） |
| 手动Mock | 灵活简单，Mock逻辑和测试代码在一起 |
| gomock | 自动生成、调用次数验证、类型安全 |
| EXPECT | Times/Return/Do/Any匹配调用期望 |
| 数据库测试 | SQLite内存（Repository层）、Mock（Service层）、Docker临时MySQL（集成测试） |
| 过度Mock | Mock纯函数、Mock太复杂的接口 → 设计问题 |

> 🚀 下一章：第109章 · 集成测试。Mock让你隔离测试了每个组件——但组件之间的协作是对的吗？Handler和Service能对接上吗？请求真的能走到数据库吗？集成测试负责验证这一切。

---
[← 上一章：106-单元测试.md](106-单元测试.md) | [下一章：108-集成测试.md →](108-集成测试.md)
