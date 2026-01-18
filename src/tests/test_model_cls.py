class ParentCls:
    model = None

    def __init__(self):
        self.session = None

    def init_1(self, session):
        self.session = session
        # self.model = model  # Атрибут экземпляра класса
        # ParentCls.model = model  # Атрибут класса

    def init_2(self, session, model):
        self.session = session
        # self.model = model  # Атрибут экземпляра класса
        ParentCls.model = model  # Атрибут класса


class ChildCls1(ParentCls):
    model = "HotelsORM11111"

    def __init__(self, session):
        super().init_1(session)


class ChildCls2(ParentCls):

    def __init__(self, session, tmp_str="HotelsORM22222"):
        super().init_2(session, tmp_str)


class ChildCls3(ParentCls):
    model = "333333"

    def __init__(self, session, tmp_str="33333HotelsORM33333"):
        super().init_2(session, tmp_str)


obj11 = ChildCls1("aa11")
print(f"{obj11.model=}")  # obj11.model='HotelsORM11111'
obj12 = ChildCls1("aa22")
print(f"{obj12.model=}")  # obj12.model='HotelsORM11111'
obj21 = ChildCls2("bb")
print(f"{obj21.model=}")  # obj21.model='HotelsORM22222'
obj31 = ChildCls3("ff33")
print(f"{obj31.model=}")  # obj31.model='333333'


print(f"{obj11.model=}")  # obj11.model='HotelsORM11111'
print(f"{obj12.model=}")  # obj12.model='HotelsORM11111'
print(f"{obj21.model=}")  # obj21.model='33333HotelsORM33333'
print(f"{obj31.model=}")  # obj31.model='333333'

print(f"{ChildCls1.model=}")  # ChildCls1.model='HotelsORM11111'
print(f"{ChildCls2.model=}")  # ChildCls2.model='33333HotelsORM33333'
print(f"{ChildCls3.model=}")  # ChildCls3.model='333333'
print(f"{ParentCls.model=}")  # ParentCls.model='33333HotelsORM33333'

ChildCls1.model = "---"

print(f"{obj11.model=}")  # obj11.model='---'
print(f"{obj12.model=}")  # obj12.model='---'
print(f"{obj21.model=}")  # obj21.model='33333HotelsORM33333'
print(f"{obj31.model=}")  # obj31.model='333333'

print(f"{ChildCls1.model=}")  # ChildCls1.model='---'
print(f"{ChildCls2.model=}")  # ChildCls2.model='33333HotelsORM33333'
print(f"{ChildCls3.model=}")  # ChildCls3.model='333333'
print(f"{ParentCls.model=}")  # ParentCls.model='33333HotelsORM33333'

obj_p1 = ParentCls()
print(f"{obj_p1.model=}")  # obj_p1.model='33333HotelsORM33333'
obj_p2 = ParentCls()
print(f"{obj_p2.model=}")  # obj_p2.model='33333HotelsORM33333'

print(f"{ChildCls1.model=}")  # ChildCls1.model='---'
print(f"{ChildCls2.model=}")  # ChildCls2.model='33333HotelsORM33333'
print(f"{ChildCls3.model=}")  # ChildCls3.model='333333'
print(f"{ParentCls.model=}")  # ParentCls.model='33333HotelsORM33333'

ParentCls.model = "gbnh"
print(f"{obj_p1.model=}")  # obj_p1.model='gbnh'
print(f"{obj_p2.model=}")  # obj_p2.model='gbnh'

print(f"{obj11.model=}")  # obj11.model='---'
print(f"{obj12.model=}")  # obj12.model='---'
print(f"{obj21.model=}")  # obj21.model='gbnh'
print(f"{obj31.model=}")  # obj31.model='333333'

print(f"{ChildCls1.model=}")  # ChildCls1.model='---'
print(f"{ChildCls2.model=}")  # ChildCls2.model='gbnh'
print(f"{ChildCls3.model=}")  # ChildCls3.model='333333'
print(f"{ParentCls.model=}")  # ParentCls.model='gbnh'

obj22 = ChildCls2("bb", "12qwsa34")

print(f"{obj11.model=}")  # obj11.model='---'
print(f"{obj12.model=}")  # obj12.model='---'
print(f"{obj21.model=}")  # obj21.model='12qwsa34'
print(f"{obj22.model=}")  # obj22.model='12qwsa34'
print(f"{obj31.model=}")  # obj31.model='333333'

print(f"{obj_p1.model=}")  # obj_p1.model='12qwsa34'
print(f"{obj_p2.model=}")  # obj_p2.model='12qwsa34'

print(f"{ChildCls1.model=}")  # ChildCls1.model='---'
print(f"{ChildCls2.model=}")  # ChildCls2.model='12qwsa34'
print(f"{ChildCls3.model=}")  # ChildCls3.model='333333'
print(f"{ParentCls.model=}")  # ParentCls.model='12qwsa34'

obj23 = ChildCls2("++тсим55--", "12**69--87")
print(f"{ChildCls1.model=}")  # ChildCls1.model='---'
print(f"{ChildCls2.model=}")  # ChildCls2.model='12**69--87'
print(f"{ChildCls3.model=}")  # ChildCls3.model='333333'
print(f"{ParentCls.model=}")  # ParentCls.model='12**69--87'

obj_p3 = ParentCls()

print(f"{obj11.model=}")  # obj11.model='---'
print(f"{obj12.model=}")  # obj12.model='---'
print(f"{obj21.model=}")  # obj21.model='12**69--87'
print(f"{obj22.model=}")  # obj22.model='12**69--87'
print(f"{obj23.model=}")  # obj23.model='12**69--87'
print(f"{obj31.model=}")  # obj31.model='333333'

print(f"{obj_p1.model=}")  # obj_p1.model='12**69--87'
print(f"{obj_p2.model=}")  # obj_p2.model='12**69--87'
print(f"{obj_p3.model=}")  # obj_p3.model='12**69--87'

print(f"{ChildCls1.model=}")  # ChildCls1.model='---'
print(f"{ChildCls2.model=}")  # ChildCls2.model='12**69--87'
print(f"{ChildCls3.model=}")  # ChildCls3.model='333333'
print(f"{ParentCls.model=}")  # ParentCls.model='12**69--87'

obj13 = ChildCls1("xcds345nhytg")
obj_p4 = ParentCls()

print(f"{obj11.model=}")  # obj11.model='---'
print(f"{obj12.model=}")  # obj12.model='---'
print(f"{obj13.model=}")  # obj13.model='---'
print(f"{obj21.model=}")  # obj21.model='12**69--87'
print(f"{obj22.model=}")  # obj22.model='12**69--87'
print(f"{obj23.model=}")  # obj23.model='12**69--87'
print(f"{obj31.model=}")  # obj31.model='333333'

print(f"{obj_p1.model=}")  # obj_p1.model='12**69--87'
print(f"{obj_p2.model=}")  # obj_p2.model='12**69--87'
print(f"{obj_p3.model=}")  # obj_p3.model='12**69--87'
print(f"{obj_p4.model=}")  # obj_p4.model='12**69--87'

print(f"{ChildCls1.model=}")  # ChildCls1.model='---'
print(f"{ChildCls2.model=}")  # ChildCls2.model='12**69--87'
print(f"{ChildCls3.model=}")  # ChildCls3.model='333333'
print(f"{ParentCls.model=}")  # ParentCls.model='12**69--87'
