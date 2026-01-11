from src.controllers.menu_controller import FortressMode



def test_integration():
    print(FortressMode)
    for m in FortressMode:
        print(m.value.title())



if __name__ == "__main__":
    test_integration()