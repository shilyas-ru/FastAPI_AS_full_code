class ParentModel:
    model = None

    def __init__(self, session):
        self.session = session
        # self.model = model  # Атрибут экземпляра класса
        # ParentModel.model = model  # Атрибут класса


class ChildModel1(ParentModel):
    model = "HotelsORM11111"

    def __init__(self, session):
        super().__init__(session)


class ChildModel2(ParentModel):
    model = "HotelsORM22222"

    def __init__(self, session):
        super().__init__(session)


obj11 = ChildModel1("aa11")
print(f"{obj11.model=}")  # obj11.model='HotelsORM11111'
obj12 = ChildModel1("aa22")
print(f"{obj12.model=}")  # obj12.model='HotelsORM11111'
obj2 = ChildModel2("bb")

print(f"{obj11.model=}")  # obj11.model='HotelsORM11111'
print(f"{obj12.model=}")  # obj12.model='HotelsORM11111'
print(f"{obj2.model=}")  # obj2.model='HotelsORM22222'

ChildModel1.model = "---"
print("----------")
print(f"{obj11.model=}")  # obj11.model='---'
print(f"{obj12.model=}")  # obj12.model='---'
print(f"{obj2.model=}")  # obj2.model='HotelsORM22222'

print("Parent")
obj_p1 = ParentModel("fdf")
print(f"{obj_p1.model=}")  # obj_p1.model=None
obj_p2 = ParentModel("4567")
print(f"{obj_p2.model=}")  # obj_p2.model=None

ParentModel.model = "gbnh"
print(f"{obj_p1.model=}")  # obj_p1.model='gbnh'
print(f"{obj_p2.model=}")  # obj_p2.model='gbnh'

print(f"{obj11.model=}")  # obj11.model='---'
print(f"{obj12.model=}")  # obj12.model='---'
print(f"{obj2.model=}")  # obj2.model='HotelsORM22222'
