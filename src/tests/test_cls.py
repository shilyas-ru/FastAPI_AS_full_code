# class ParentCls:
#     model = None
#
#     def __init__(self, session, model):
#         self.session = session
#         # self.model = model  # Атрибут экземпляра класса
#         ParentCls.model = model  # Атрибут класса
#
#
# class ChildCls1(ParentCls):
#
#     def __init__(self, session):
#         super().__init__(session, "HotelsORM11111")
#
#
# class ChildCls2(ParentCls):
#
#     def __init__(self, session):
#         super().__init__(session, "HotelsORM22222")
#
#
# obj11 = ChildCls1("aa11")
# print(f"{obj11.model=}")  # obj11.model='HotelsORM11111'
# obj12 = ChildCls1("aa22")
# print(f"{obj12.model=}")  # obj12.model='HotelsORM11111'
# obj2 = ChildCls2("bb")
#
# print(f"{obj11.model=}")  # obj11.model='HotelsORM22222'
# print(f"{obj12.model=}")  # obj12.model='HotelsORM22222'
# print(f"{obj2.model=}")  # obj2.model='HotelsORM22222'
#
# ChildCls1.model = "---"
#
# print(f"{obj11.model=}")  # obj11.model='---'
# print(f"{obj12.model=}")  # obj12.model='---'
# print(f"{obj2.model=}")  # obj2.model='HotelsORM22222'
#
# obj_p1 = ParentCls("fdf", "11")
# print(f"{obj_p1.model=}")  # obj_p1.model='11'
# obj_p2 = ParentCls("fdf", "22")
# print(f"{obj_p2.model=}")  # obj_p2.model='22'
#
# ParentCls.model = "gbnh"
# print(f"{obj_p1.model=}")  # obj_p1.model='gbnh'
# print(f"{obj_p2.model=}")  # obj_p2.model='gbnh'
#
# print(f"{obj11.model=}")  # obj11.model='---'
# print(f"{obj12.model=}")  # obj12.model='---'
# print(f"{obj2.model=}")  # obj2.model='gbnh'

def f():
    s = 'foo'
    loc = locals()
    print(loc)  # {'s': 'foo'}

    x = 20
    print(loc)  # {'s': 'foo'}

    loc['s'] = 'bar'
    print(s)  # foo

    loc = locals()
    print(loc)  # {'s': 'foo', 'loc': {...}, 'x': 20}

f()
