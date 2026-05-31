# 46. 数组与ArrayList源码分析

> 🏢 你去银行租了一排保险柜，柜号001到100。你知道003号柜里存着房产证，直奔003号，5秒拿出。你突然想再加一个柜子——对不起，这排只有100个，要加就得换一排更大的。——这就是数组：**连续内存 + 随机访问极快 + 扩容代价高**。

---

## 46.1 数组的物理本质

Java数组在内存中是一块**连续的**空间：

```
内存地址:  1000  1004  1008  1012  1016
         ┌──────┬──────┬──────┬──────┬──────┐
         │  10  │  20  │  30  │  40  │  50  │
         └──────┴──────┴──────┴──────┴──────┘
索引:       0      1      2      3      4
```

**为什么`arr[3]`是O(1)？**
```
目标地址 = 起始地址 + 索引 × 每个元素大小
        = 1000 + 3 × 4
        = 1012           ← 一次乘法+加法，直接拿到
```

不需要遍历，不需要搜索，直接计算地址，拿到数据。这就是**随机访问（Random Access）**。

**数组的两大特性**：
1. **长度固定**：`int[] arr = new int[5]`，这5个位置在内存中连续分配，宣告即确定
2. **类型一致**：所有元素占用相同字节数，所以才能用公式计算地址

---

## 46.2 数组的基本操作（Java实现）

```java
public class ArrayDemo {
    public static void main(String[] args) {
        // 创建：必须指定长度
        int[] arr = new int[5];

        // 写入：通过索引 O(1)
        arr[0] = 10;
        arr[1] = 20;
        arr[2] = 30;
        arr[3] = 40;
        arr[4] = 50;

        // 读取：通过索引 O(1)
        int third = arr[3];  // 40

        // 查找某个值：必须遍历 O(n)
        int target = 30;
        int index = -1;
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) {
                index = i;
                break;
            }
        }
        System.out.println("30在索引: " + index);  // 2

        // 在中间插入（需要搬移数据）O(n)
        // 在索引2插入99，需要把索引2及之后的元素后移
        int[] newArr = new int[arr.length + 1];
        int insertPos = 2;
        for (int i = 0; i < insertPos; i++) {
            newArr[i] = arr[i];
        }
        newArr[insertPos] = 99;
        for (int i = insertPos; i < arr.length; i++) {
            newArr[i + 1] = arr[i];
        }
        // newArr: [10, 20, 99, 30, 40, 50]
    }
}
```

---

## 46.3 ArrayList — 可自动扩容的数组

因为原生数组长度固定，Java提供了`ArrayList`——内部还是数组，但能自动扩容。

### 源码核心字段

打开JDK的`ArrayList.java`，你看到三个核心成员：

```java
public class ArrayList<E> extends AbstractList<E> {
    // 真正存数据的数组
    transient Object[] elementData;

    // 当前已存放的元素个数（不是数组容量！）
    private int size;

    // 默认初始容量
    private static final int DEFAULT_CAPACITY = 10;
}
```

关键在于：**`size` ≠ `elementData.length`**。

```java
ArrayList<String> list = new ArrayList<>();
// elementData.length = 10（默认容量）
// size = 0（还没放任何东西）

list.add("A");
list.add("B");
// elementData.length = 10（还是10，没扩容）
// size = 2（放了2个元素）
```

### add() 方法的完整过程

```java
public boolean add(E e) {
    modCount++;
    add(e, elementData, size);
    return true;
}

private void add(E e, Object[] elementData, int s) {
    if (s == elementData.length)
        elementData = grow();    // 满了，扩容！
    elementData[s] = e;          // 放入元素
    size = s + 1;                // size加1
}
```

**扩容机制 grow() 核心逻辑：**

```java
private Object[] grow() {
    return grow(size + 1);
}

private Object[] grow(int minCapacity) {
    int oldCapacity = elementData.length;
    if (oldCapacity > 0 || elementData != DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {
        int newCapacity = ArraysSupport.newLength(
            oldCapacity,
            minCapacity - oldCapacity,     // 最小增长量
            oldCapacity >> 1               // 首选增长量：oldCapacity / 2
        );
        return elementData = Arrays.copyOf(elementData, newCapacity);
    } else {
        return elementData = new Object[Math.max(DEFAULT_CAPACITY, minCapacity)];
    }
}
```

**扩容公式**：`新容量 = 旧容量 + 旧容量 / 2`，即**1.5倍扩容**。

**扩容过程分解**：
1. 创建新的更大数组（容量为原来的1.5倍）
2. 把旧数组的元素逐个拷贝到新数组
3. 旧数组被GC回收
4. `elementData`指向新数组

```java
// 扩容的视觉过程
// 初始：elementData = [A, B, C, D, E, F, G, H, I, J]  ← size=10, 满了
// 第11次add("K")触发扩容：
//   1. newCapacity = 10 + 10/2 = 15
//   2. 创建新数组 [null×15]
//   3. 拷贝：[A, B, C, D, E, F, G, H, I, J, null, null, null, null, null]
//   4. elementData指向新数组
//   5. 放入"K"：[A, B, C, D, E, F, G, H, I, J, K, null, null, null, null]
//   size = 11
```

### ArrayList 各操作的时间复杂度

| 操作 | 时间复杂度 | 原因 |
|---|---|---|
| `get(index)` | O(1) | 直接计算地址 |
| `set(index, e)` | O(1) | 直接写地址 |
| `add(e)`（末尾追加） | **均摊O(1)** | 偶尔扩容O(n)，但平均几乎是O(1) |
| `add(index, e)`（中间插入） | O(n) | 需要后移index到末尾的所有元素 |
| `remove(index)` | O(n) | 需要前移index+1到末尾的所有元素 |
| `contains(e)` | O(n) | 需要遍历查找 |
| `indexOf(e)` | O(n) | 需要遍历查找 |

> 🤔 想多一点：**均摊O(1)** 是什么意思？假设从容量10开始扩容，10→15→22→33→49→73。每次扩容拷贝元素，但平摊到每次add上，开销几乎是常数。好比搬家：10年搬一次，平摊到每天的成本近乎为零。

---

## 46.4 正确使用ArrayList的最佳实践

### ✅ 已知数据量时，指定初始容量

```java
// ❌ 糟糕：知道要存10000条，用默认容量（10）
ArrayList<String> list = new ArrayList<>();
for (int i = 0; i < 10000; i++) {
    list.add("item" + i);
}
// 扩容路径：10→15→22→33→...约需扩容15次，每次拷贝O(n)，浪费大量时间

// ✅ 正确：预估容量
ArrayList<String> list = new ArrayList<>(10000);
for (int i = 0; i < 10000; i++) {
    list.add("item" + i);
}
// 0次扩容，直接存
```

### ✅ 频繁查找用HashSet，频繁索引访问用ArrayList

```java
// ❌ 错误：频繁用contains查重
ArrayList<String> list = new ArrayList<>();
for (String item : hugeList) {
    if (!list.contains(item)) {    // O(n) 每次都遍历
        list.add(item);
    }
}
// 总复杂度 O(n²)

// ✅ 正确：用HashSet
HashSet<String> set = new HashSet<>();
for (String item : hugeList) {
    set.add(item);                 // O(1)
}
// 总复杂度 O(n)
```

### ✅ 需要删除元素时，从后往前遍历

```java
// ❌ 错误：从前往后删除，索引会跳位
ArrayList<Integer> list = new ArrayList<>(List.of(1, 2, 3, 2, 4));
for (int i = 0; i < list.size(); i++) {
    if (list.get(i) == 2) {
        list.remove(i);    // 删除后，后面的元素前移，但i继续++，会漏掉元素
    }
}
// 结果：[1, 3, 2, 4] ← 漏了一个2！

// ✅ 正确方式1：从后往前遍历
for (int i = list.size() - 1; i >= 0; i--) {
    if (list.get(i) == 2) {
        list.remove(i);
    }
}

// ✅ 正确方式2：用Iterator
Iterator<Integer> it = list.iterator();
while (it.hasNext()) {
    if (it.next() == 2) {
        it.remove();
    }
}

// ✅ 正确方式3：用removeIf（Java 8+）
list.removeIf(x -> x == 2);
```

---

## 46.5 ArrayList vs 数组：何时用哪个

| 场景 | 用数组 | 用ArrayList |
|---|---|---|
| 长度完全确定、永不变 | ✅ | 也行 |
| 长度未知、动态变化 | ❌ | ✅ |
| 需要泛型（如存`List<User>`） | ❌ | ✅ |
| 追求极致性能（如底层库） | ✅ | ❌（有装箱开销）|
| 基本类型大量计算（int/long等） | ✅ | ❌（自动装箱）|

> 🤔 想多一点：为什么基本类型用ArrayList有装箱开销？因为`ArrayList<int>`不合法（泛型不支持基本类型），必须写`ArrayList<Integer>`，每次add都要把int装箱成Integer，每次get再拆箱回int，高频场景下性能差距明显。

---

## 46.6 ❌ 常见错误

| 错误 | 后果 | 正确做法 |
|---|---|---|
| `ArrayList`不设初始容量 | 大量扩容浪费性能 | 预估值传入构造函数 |
| 在增强for循环中删除元素 | `ConcurrentModificationException` | 用Iterator.remove() 或 removeIf |
| 用`list.contains()`做高频查重 | O(n²)复杂度 | 改用HashSet |
| 把`size`和`capacity`混淆 | 理解错误 | size是元素数，capacity是数组长度 |
| 在循环中频繁`add(index, e)` | 每次O(n)，总计O(n²) | 用LinkedList或先add末尾再Collections.sort |

---

## 小结

| 概念 | 解释 |
|---|---|
| 数组物理结构 | 连续内存，通过`首地址+索引×元素大小`定位，O(1) |
| ArrayList扩容 | 1.5倍增长，底层`Arrays.copyOf()`，均摊O(1) |
| get/set | O(1) — 随机访问 |
| add(末尾) | 均摊O(1) |
| add(index)/remove(index) | O(n) — 需要搬移元素 |
| contains/indexOf | O(n) — 需要遍历 |
| 最佳实践 | 预估容量、频繁查重用HashSet、删除用Iterator |

## 自测题

1. 已知`ArrayList`初始容量10，连续添加15个元素，总共经历了几次扩容？写出每次扩容后的容量。
2. 为什么ArrayList的`add(E e)`（末尾追加）是**均摊O(1)**而不是纯O(1)？
3. 下列代码有什么问题？如果list初始为`[1,2,2,3,2,4]`，运行后结果是什么？
```java
ArrayList<Integer> list = new ArrayList<>(List.of(1, 2, 2, 3, 2, 4));
for (int i = 0; i < list.size(); i++) {
    if (list.get(i) == 2) {
        list.remove(i);
    }
}
System.out.println(list);
```