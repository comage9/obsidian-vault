---
name: react-table-inline-editing
description: React 테이블 셀 직접 편집 + Combobox 자동완성 패턴 (shadcn/ui + TanStack Query)
triggers:
  - "셀 직접 편집"
  - "더블클릭하여 편집"
  - "테이블에서 바로 입력"
  - "Combobox"
  - "자동완성"
  - "PopoverCommand"
---

# react-table-inline-editing

## 개요
React 테이블 행 컴포넌트에서 셀 직접 편집(더블클릭/클릭 → 인라인 Input 또는 Combobox 팝업)을 구현하는 패턴.

**사용처:** shadcn/ui + TanStack Query 환경의 생산 계획, 재고管理等 데이터 테이블

## 프로젝트
- `/home/comage/coding/VF/frontend/client/src/pages/production-plan.tsx` — 실제 구현 참고

## 핵심 패턴

### 1. 테이블 행 컴포넌트 상태
```tsx
const [editingCell, setEditingCell] = useState<keyof ProductionItem | null>(null);
const [cellValue, setCellValue] = useState('');

const startEdit = (field, currentValue) => {
  setEditingCell(field);
  setCellValue(String(currentValue ?? ''));
};

const commitEdit = () => {
  if (editingCell !== null) {
    onFieldChange(row.id, editingCell, cellValue);
    setEditingCell(null);
    setCellValue('');
  }
};

const cancelEdit = () => {
  setEditingCell(null);
  setCellValue('');
};

const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === 'Enter') commitEdit();
  else if (e.key === 'Escape') cancelEdit();
};
```

### 2. 부모 → 자식 인터페이스
```tsx
interface SortableRowProps {
  row: ProductionItem;
  onFieldChange: (id: number, field: keyof ProductionItem, value: string | number) => void;
  uniqueProductNames?: string[];  // Combobox용
  specs?: MasterSpec[];            // Combobox 필터링용
  // ... 기존 props
}
```

### 3. 부모 핸들러
```tsx
const handleFieldChange = useCallback((id: number, field: keyof ProductionItem, value: string | number) => {
  const updates: Partial<ProductionItem> = {};
  if (field === 'quantity' || field === 'unitQuantity') {
    updates[field] = Number(value) || 0;
  } else {
    updates[field] = value as string;
  }
  updateMutation.mutate({ id, updates });
}, [updateMutation]);
```

### 4. 인라인 편집 셀 (문자/숫자)
```tsx
<td className="py-3 px-4 text-right">
  {editingCell === 'quantity' ? (
    <Input
      className="h-7 w-20 inline-block text-right"
      value={cellValue}
      onChange={(e) => setCellValue(e.target.value)}
      onBlur={commitEdit}
      onKeyDown={handleKeyDown}
      autoFocus
    />
  ) : (
    <span
      className="cursor-pointer hover:bg-muted/50 rounded px-1"
      onDoubleClick={() => startEdit('quantity', row.quantity || 0)}
    >
      {NUMBER_FORMATTER.format(row.quantity || 0)}
    </span>
  )}
</td>
```

### 5. Combobox 셀 (Popover + Command)
```tsx
<td>
  <Popover open={editingCell === 'productName'} onOpenChange={(open) => !open && cancelEdit()}>
    <PopoverTrigger asChild>
      <button onClick={() => startEdit('productName', row.productName || '')}>
        <div className="font-medium">{row.productName || '비어있음'}</div>
        {row.productNameEng && <div className="text-xs text-muted-foreground">{row.productNameEng}</div>}
      </button>
    </PopoverTrigger>
    {/* ⚠️ bg-background 필수 — 안 하면 투명 배경을 가짐 */}
    <PopoverContent className="w-[320px] p-0 bg-background border shadow-lg" align="start">
      {/* ⚠️ key={...}로 강제 리마운트 — 안 하면 defaultValue가 팝업 재열 때 안 읽힘 */}
      <Command shouldFilter={false} key={editingCell === 'productName' ? `edit-${row.id}` : undefined}>
        {/* ⚠️ cmdk CommandInput은 항상 uncontrolled — value=不许, defaultValue만 사용 */}
        <CommandInput
          placeholder="검색 또는 직접 입력..."
          defaultValue={cellValue}
          onValueChange={(val) => setCellValue(val)}
          autoFocus
        />
        <CommandList>
          {uniqueProductNames
            .filter(name => !cellValue || name.toLowerCase().includes(cellValue.toLowerCase()))
            .slice(0, 20)
            .map(name => (
              <CommandItem key={name} value={name} onSelect={() => {
                onFieldChange(row.id, 'productName', name);
                setEditingCell(null);
                setCellValue('');
              }}>
                <Check className="mr-2 h-4 w-4 opacity-50" />
                <span className="flex-1">{name}</span>
              </CommandItem>
            ))}
          {cellValue && (
            <CommandItem key="__direct__" value={cellValue} onSelect={() => {
              onFieldChange(row.id, 'productName', cellValue);
              setEditingCell(null);
              setCellValue('');
            }} className="border-t mt-1 pt-1 text-muted-foreground">
              ▶ 직접 입력: <strong>"{cellValue}"</strong>
            </CommandItem>
          )}
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</td>
```

## 공통 pitfall
- `<td>` 닫는 태그 누락 → JSX parse error (400:4)
- `onFieldChange` props 누락 → 컴파일 에러
- `uniqueProductNames`/`specs` props 부모에서 안 넘김
- 빌드에서 error 없으면 dev server도 대부분 정상 (200)
- Dev server 죽으면 `npm run build`로 검증 먼저
- **cmdk CommandInput은 항상 uncontrolled** — `value` prop 사용 시 React 경고 (`Primitive.input contains an input of type text with both value and defaultValue`) → 반드시 `defaultValue` + `key` 트릭 사용
- **PopoverContent 배경 투명** — Radix 기본 스타일 때문에 `bg-background border shadow-lg` 필수
- **팝업 재열 때 초기값 안 읽힘** — `Command`에 `key={...}`로 강제 리마운트해야 `defaultValue`가 다시 적용됨

## Combobox 변환 시 blank 페이지 문제

Combobox로 변환 후 page가 blank로 보이면 UI 문제가 아니라 **TanStack Query 데이터 문제**일 수 있음:

1. **필드명 불일치** — API가 snake_case(`product_name`)를 반환하는데 Combobox가 camelCase(`productName`)를 읽으면 `uniqueProductNames`가 빈 배열 → filter 결과도 빈 배열 → Combobox 렌더링 실패 → page blank
2. **디버깅 순서**:
   - `npm run build`로 컴파일 에러 먼저排除
   - 브라우저 콘솔 + Network 탭에서 API 응답 확인
   - React DevTools에서 `uniqueProductNames` 배열 길이 확인 (0이면 데이터源 문제)
3. **해결**: 데이터读取 코드를 실제 API 필드명(`product_name`)에 맞추거나, 데이터 변환 계층 추가
4. **임시 회피**: `git stash`로 변경사항 보관 → 원래 코드로 복구 → 데이터問題 따로 해결

```bash
cd /home/comage/coding/VF/frontend/client && git stash   # 변경사항 보관
git stash pop                                              # 복구
```

## 검증
```bash
cd /home/comage/coding/VF/frontend/client && npm run build
```
error 없으면 ✅
