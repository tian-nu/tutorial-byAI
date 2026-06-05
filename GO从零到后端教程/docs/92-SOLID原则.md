# 第92章 · SOLID原则

> "设计模式是'招式'，SOLID原则（面向对象设计的五个基本原则，详见附录I）是'心法'。掌握了心法，你不需要死记硬背23种模式——你会在写代码时自然用出合适的结构。本章每个原则都包含一个反例（你可能正在这样写的代码）和一个正例（改完以后的样子），让你直观感受到SOLID带来的变化。"

---

## 92.1 单一职责原则（SRP）

> **一个类/模块只应该有一个被修改的理由。**

### 比喻：公司岗位分工

一家小公司刚起步时可能一个人同时干财务、HR、行政的活。公司只有5个人时这没问题——总共也没多少账要做。但公司长到500人时，如果还是"老王既管工资又管招聘又管报税"——他哪天请假了，整个公司瘫痪。而且他很容易犯错——管工资的时候满脑子招聘的事。

代码也一样：一个小函数里面什么都做，规模小的时候没问题。规模一大，任何修改都可能牵一发动全身。

### 反例：一个"万能订单服务"

```go
type OrderService struct {
	db *sql.DB
}

func (s *OrderService) CreateOrder(req CreateOrderRequest) error {
	tx, _ := s.db.Begin()

	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()

	_, err := tx.Exec("INSERT INTO orders (...) VALUES (...)")
	if err != nil {
		tx.Rollback()
		return err
	}

	_, err = tx.Exec("UPDATE inventory SET stock = stock - ? WHERE product_id = ?",
		req.Quantity, req.ProductID)
	if err != nil {
		tx.Rollback()
		return err
	}

	receipt := fmt.Sprintf("订单%s已创建，金额%.2f", orderID, req.Amount)
	err = sendSMS(req.UserPhone, receipt)
	if err != nil {
		return err
	}

	err = sendEmail(req.UserEmail, "订单确认", receipt)
	if err != nil {
		return err
	}

	tx.Commit()
	return nil
}
```

这个 `CreateOrder` 同时干了三件事：操作数据库（订单+库存）、发短信、发邮件。修改库存逻辑可能会影响订单创建逻辑，修改短信模板可能要改订单服务的代码——这就是"多个被修改的理由"。

### 正例：职责分离

```go
type OrderRepository struct {
	db *sql.DB
}

func (r *OrderRepository) Create(order Order) error {
	_, err := r.db.Exec("INSERT INTO orders (...) VALUES (...)", order.ID, order.UserID, order.Amount)
	return err
}

type InventoryService struct {
	repo *InventoryRepository
}

func (s *InventoryService) Deduct(productID string, quantity int) error {
	return s.repo.Deduct(productID, quantity)
}

type NotificationService struct {
	sms   *SMSClient
	email *EmailClient
}

func (s *NotificationService) SendOrderConfirmation(order Order) {
	s.sms.Send(order.UserPhone, "订单"+order.ID+"已创建")
	s.email.Send(order.UserEmail, "订单确认", "您的订单已创建")
}

type OrderService struct {
	orderRepo      *OrderRepository
	inventory      *InventoryService
	notification   *NotificationService
}

func (s *OrderService) CreateOrder(req CreateOrderRequest) error {
	order := Order{ID: generateID(), UserID: req.UserID, Amount: req.Amount}

	err := s.orderRepo.Create(order)
	if err != nil {
		return err
	}

	err = s.inventory.Deduct(req.ProductID, req.Quantity)
	if err != nil {
		return err
	}

	go s.notification.SendOrderConfirmation(order)

	return nil
}
```

现在：
- 修改短信模板→只改 `NotificationService`
- 修改库存策略→只改 `InventoryService`
- 修改订单表结构→只改 `OrderRepository`

每个模块只有一个被修改的理由。

---

## 92.2 开闭原则（OCP）

> **对扩展开放，对修改关闭。意味着新增功能时，不应该修改已有代码，而是新增代码。**

### 比喻：USB接口

你的电脑有一个USB接口。你想接鼠标→插上。想接键盘→插上。想接U盘→插上。电脑不需要因为"新增了键盘支持"而改任何一个零件——它只定义了"USB接口"这个规范，所有符合规范的设备都能即插即用。

这就是OCP：电脑对扩展开放（可以接任意USB设备），对修改关闭（不需要拆开电脑改线路）。

### 反例：每次新增功能都要改核心代码

```go
func CalculateShipping(order Order) float64 {
	switch order.Courier {
	case "SF":
		return order.Weight * 10
	case "YTO":
		return order.Weight * 6
	case "ZTO":
		return order.Weight * 5
	default:
		return order.Weight * 8
	}
}
```

每次新增圆通顺丰极兔韵达，都要改这个 `CalculateShipping` 函数。加着加着这个switch就有二十个case了——这就是"对修改不关闭"。

### 正例：用接口扩展

```go
type ShippingCalculator interface {
	Calculate(weight float64) float64
}

type SFExpress struct{}

func (s *SFExpress) Calculate(weight float64) float64 {
	return weight * 10
}

type YTOExpress struct{}

func (y *YTOExpress) Calculate(weight float64) float64 {
	return weight * 6
}

func CalculateShipping(order Order, calculator ShippingCalculator) float64 {
	return calculator.Calculate(order.Weight)
}
```

新来一个快递公司"极兔"：

```go
type JituExpress struct{}

func (j *JituExpress) Calculate(weight float64) float64 {
    return weight * 3.5
}
```

只需要新增一个类型，不需要改 `CalculateShipping` 一行代码。核心逻辑对修改关闭了，但通过接口对扩展开放了。

---

## 92.3 里氏替换原则（LSP）

> **子类必须能够完全替代父类。程序的行为不应该因为替换了子类而改变。**

### 比喻：鸭子和企鹅

你说"所有鸟都会飞"，然后设计了一个 `Bird.Fly()` 方法。鸵鸟是鸟→继承Bird→但鸵鸟不会飞→`Fly()` 抛异常。这就违反了LSP——鸵鸟不能替代鸟在"飞"这个操作上。

问题的根源不是"鸵鸟不会飞"，而是你错误地定义了"鸟=会飞"。正确的做法是：把"飞"的能力抽象为接口，只有能飞的鸟才实现它。

### 反例：Go里的"伪继承"

Go没有继承，但LSP的概念同样适用——当某个接口的实现表现出"出乎意料"的行为时，就违反了LSP。

```go
type Cache interface {
	Get(key string) (string, error)
	Set(key string, value string) error
}

type RedisCache struct{}

func (r *RedisCache) Get(key string) (string, error) {
	return "", nil
}

func (r *RedisCache) Set(key string, value string) error {
	return nil
}

type BrokenCache struct{}

func (b *BrokenCache) Get(key string) (string, error) {
	return "", fmt.Errorf("这个缓存还没有实现")
}

func (b *BrokenCache) Set(key string, value string) error {
	panic("不支持Set操作")
}
```

`BrokenCache` 实现了 `Cache` 接口，但行为完全不符合预期——Get永远返回错误，Set直接panic。如果某个函数依赖 `Cache` 接口工作，传入 `BrokenCache` 会直接搞崩系统。

### 正例：要么不实现接口，要么正确实现

```go
type Cache interface {
	Get(key string) (string, error)
	Set(key string, value string) error
}

type RedisCache struct{}

func (r *RedisCache) Get(key string) (string, error) {
	data, err := redisClient.Get(ctx, key).Result()
	if err == redis.Nil {
		return "", ErrNotFound
	}
	return data, err
}

func (r *RedisCache) Set(key string, value string) error {
	return redisClient.Set(ctx, key, value, 0).Err()
}

type MemCache struct{}

func (m *MemCache) Get(key string) (string, error) {
	val, ok := m.data[key]
	if !ok {
		return "", ErrNotFound
	}
	return val, nil
}

func (m *MemCache) Set(key string, value string) error {
	m.data[key] = value
	return nil
}
```

`RedisCache` 和 `MemCache` 都正确实现了 `Cache` 接口——同一个调用方可以无缝切换两者，行为完全一致。

---

## 92.4 接口隔离原则（ISP）

> **不应该强迫调用方依赖它不使用的方法。大而全的接口应该拆成小而精的多个接口。**

### 比喻：多功能遥控器

你家有空调、电视、音响三个遥控器。某天厂商说"我们把三个合成一个超级遥控器！"你拿起遥控器——上面有120个按钮，你调个空调温度要在120个按钮里找到温度键。

接口隔离原则说：**我宁可要三个各管各的遥控器，也不要一个"万能"遥控器。**

### 反例：大肥接口

```go
type OrderRepository interface {
	Create(order Order) error
	Update(order Order) error
	Delete(id string) error
	GetByID(id string) (*Order, error)
	ListByUser(userID string) ([]Order, error)
	ListByDateRange(start, end time.Time) ([]Order, error)
	GetStatistics() (*OrderStats, error)
	ExportToCSV(writer io.Writer) error
	Archive() error
}
```

后台管理页面需要全部9个方法。但用户端的"我的订单"页面只需要 `ListByUser` 和 `GetByID`。

如果你用这一个大接口：用户端的测试需要Mock全部9个方法——即便它只用了2个。而且一眼看不出"这个服务到底需要什么"。

### 正例：按需拆分

```go
type OrderReader interface {
	GetByID(id string) (*Order, error)
	ListByUser(userID string) ([]Order, error)
}

type OrderWriter interface {
	Create(order Order) error
	Update(order Order) error
	Delete(id string) error
}

type OrderReporter interface {
	ListByDateRange(start, end time.Time) ([]Order, error)
	GetStatistics() (*OrderStats, error)
	ExportToCSV(writer io.Writer) error
}

type OrderArchiver interface {
	Archive() error
}
```

现在：
- 用户端只依赖 `OrderReader`
- 下单服务依赖 `OrderReader` + `OrderWriter`
- 后台报表依赖 `OrderReporter`
- 定时任务依赖 `OrderArchiver`

每个调用方只看到它需要的方法。测试Mock量大幅减少，依赖关系清晰可见。

---

## 92.5 依赖反转原则（DIP）

> **高层模块不应该依赖低层模块，两者都应该依赖抽象（接口）。**

### 比喻：插座和电器

你的台灯不应该焊接在墙里的电线上。正确的做法是：墙上装一个标准插座（接口），台灯通过插头（实现接口）插入。你想换LED灯、日光灯、甚至接一个风扇——只要符合插座标准，都能用。

台灯不依赖"墙里的电线"，插座不依赖"台灯的品牌"——两者都依赖"插座标准"这个抽象。

### 反例：高层直接依赖低层

```go
type UserService struct {
	db *sql.DB
}

func (s *UserService) GetUser(id string) (*User, error) {
	row := s.db.QueryRow("SELECT * FROM users WHERE id = ?", id)
	var user User
	err := row.Scan(&user.ID, &user.Name, &user.Email)
	return &user, err
}

func (s *UserService) CreateUser(user User) error {
	_, err := s.db.Exec("INSERT INTO users (...) VALUES (...)", user.ID, user.Name, user.Email)
	return err
}
```

`UserService`（高层业务逻辑）直接依赖 `*sql.DB`（低层数据库细节）。如果将来要换数据库、加缓存、加日志——全要改 `UserService` 的代码。

### 正例：依赖接口

```go
type UserRepository interface {
	FindByID(id string) (*User, error)
	Save(user User) error
}

type MySQLUserRepository struct {
	db *sql.DB
}

func (r *MySQLUserRepository) FindByID(id string) (*User, error) {
	row := r.db.QueryRow("SELECT * FROM users WHERE id = ?", id)
	var user User
	err := row.Scan(&user.ID, &user.Name, &user.Email)
	return &user, err
}

func (r *MySQLUserRepository) Save(user User) error {
	_, err := r.db.Exec("INSERT INTO users (...) VALUES (...)", user.ID, user.Name, user.Email)
	return err
}

type UserService struct {
	repo UserRepository
}

func (s *UserService) GetUser(id string) (*User, error) {
	return s.repo.FindByID(id)
}

func (s *UserService) CreateUser(user User) error {
	return s.repo.Save(user)
}
```

现在 `UserService` 只依赖 `UserRepository` 接口。换数据库？写一个新的实现就行。加缓存？写一个 `CachedUserRepository` 包装。测试？Mock `UserRepository` 即可。

---

🤔 **想多一点**：SOLID是规矩还是建议？

有人把SOLID奉为教条，每个项目都要逐条对照。但过度遵守SOLID会导致另一个极端——**过度设计**。一个只有200行代码的内部工具，你把它拆成5个接口8个类——这就叫"为了SOLID而SOLID"。

Robert C. Martin（SOLID的提出者）自己也说过：**"You should not start with SOLID. You should refactor towards SOLID."**

翻译：不要一开始就想着"我要按SOLID设计"，而是先写能跑的代码，当代码开始变得难以维护时，**向SOLID的方向重构**。

什么时候该重构？
- 一个函数超过50行 → 考虑SRP
- 每次加新功能都要改老代码 → 考虑OCP
- 测试时Mock疯了 → 考虑ISP
- 换一个数据库要改几十个文件 → 考虑DIP

SOLID是"你感觉代码味道不对时的诊断手册"，不是"项目启动前的设计蓝图"。

---

## 本章小结

| 原则 | 核心问题 | 判断方法 |
|------|---------|---------|
| SRP 单一职责 | 这个模块干了太多事 | "这个类为什么会被修改？"答案多于1个→违反 |
| OCP 开闭原则 | 加功能就要改老代码 | 新增功能时，老代码动了几行？ |
| LSP 里氏替换 | 实现看起来能用但行为异常 | 替换实现后程序行为一致吗？ |
| ISP 接口隔离 | 被迫实现不需要的方法 | Mock测试时有没有在Mock用不到的方法？ |
| DIP 依赖反转 | 业务逻辑直接依赖数据库/网络 | 能不能不启动数据库就测试业务逻辑？ |

> 🚀 下一章：掌握了设计模式和SOLID原则，你的代码质量已经上了一个台阶。接下来我们要走向更大的战场——微服务架构。单体应用什么时候该拆？怎么拆？服务之间怎么"找到彼此"？

---
[← 上一章：91-设计模式（Go实现）.md](91-设计模式（Go实现）.md) | [下一章：93-微服务基础.md →](93-微服务基础.md)
