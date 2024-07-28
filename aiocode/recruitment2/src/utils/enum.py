
'''
使用说明：
    0.定义说明
        class Platform(Const):
            属性 = (值, 说明)
            属性 = {'value':值, 'label':说明}
            属性 = 说明 # 值 与 属性 相同的情况下(值与属性都定义为字符串)

    1.定义枚举类， 直接继承此文件的 Const 类即可， 如：

        # 属性 = (值, 说明)  的定义模式,且值是整形
        class Platform(Const):
            ios = (1, 'IOS')
            android = (2, 'ANDROID')
            wp = (3, 'WP')

        # 属性 = (值, 说明)  的定义模式,且值是字符串
        class LocationType(Const):
            asia = ('Asia', u'亚洲')
            europe = ('Europe', u'欧洲')
            america = ('America', u'美洲')
            australia = ('Australia', u'澳洲')

        # 属性 = {'value':值, 'label':说明}  的定义模式,值是整形或者字符串都允许
        class LocationType2(Const):
            asia = {'value':'Asia', 'label':'亚洲'}
            europe = {'value':'Europe', 'label':'欧洲'}
            america = {'value':'America', 'label':'美洲'}
            australia = {'value':'Australia', 'label':'澳洲'}

        # 属性 = 说明  的定义模式,且值跟属性一样
        class LocationType3(Const):
            asia = u'亚洲'
            europe = u'欧洲'
            america = '美洲'
            australia = '澳洲'

    3.用来判断时， 直接点出枚举类对应的值即可：

        mo = TestModel()
        if mo.platform == Platform.android: print '这是安卓用户'


    4.获取对应的说明时， 用类的“get_FEILD_display”即可：

        mo = TestModel()
        plat_name = mo.get_platform_display()

        页面展示时：
        {{ object.get_platform_display }}


    5.获取对应的说明， 也可以由枚举类直接获取(用 attrs_, values_, labels_, labels_to_values_, items_ 五个属性)：

        print( Platform.ios == 1 and Platform.android == 2 ) # 打印: True

        print( Platform.attrs_[2] == 'ANDROID' ) # 打印: True
        print( Platform.attrs_ ) # 打印: {1: 'IOS', 2: 'ANDROID', 3: 'WP'}
        # 枚举类.attrs_ 返回 {值:说明}

        print( Platform.labels_to_values_['ANDROID'] == 2 ) # 打印: True
        print( Platform.labels_to_values_ ) # 打印: {'ANDROID': 2, 'IOS': 1, 'WP': 3}
        # 枚举类.labels_to_values_ 返回 {说明:值} 。 与 attrs_ 正好相反

        print( Platform.values_['ios'] == 1 ) # 打印: True
        print( Platform.values_ ) # 打印: {'android': 2, 'ios': 1, 'wp': 3}
        # 枚举类._values 返回 {属性:值}

        print( Platform.labels_['ios'] == 'IOS' ) # 打印: True
        print( Platform.labels_ ) # 打印: {'android': 'ANDROID', 'ios': 'IOS', 'wp': 'WP'}
        # 枚举类.labels_ 返回 {属性:说明}

        print( Platform() ) # 打印: [(1, 'IOS'), (2, 'ANDROID'), (3, 'WP')]
        print( Platform.items_ ) # 打印: [(1, 'IOS'), (2, 'ANDROID'), (3, 'WP')]
        # 枚举类.items_ 返回 [(值,说明), (值,说明)]
'''


class ConstType(type):
    def __new__(mcs, name, bases, attrs):
        _values = {}    # {属性:值}
        _labels = {}    # {属性:说明}
        _attrs = {}     # {值:说明}
        _labels_to_values = {}  # {说明:值}

        for k, v in attrs.items():
            if k.startswith('__'):
                continue
            if isinstance(v, (tuple, list)) and len(v) == 2:
                _values[k] = v[0]
                _labels[k] = v[1]
                _attrs[v[0]] = v[1]
                _labels_to_values[v[1]] = v[0]
            elif isinstance(v, dict) and 'label' in v and 'value' in v:
                _values[k] = v['value']
                _labels[k] = v['label']
                _attrs[v['value']] = v['label']
                _labels_to_values[v['label']] = v['value']
            elif isinstance(v, str):
                _values[k] = k
                _labels[k] = v
                _attrs[k] = v
                _labels_to_values[v] = k
            else:
                _values[k] = v
                _labels[k] = v

        obj = type.__new__(mcs, name, bases, _values)
        obj.values_ = _values
        obj.labels_ = _labels
        obj.labels_to_values_ = _labels_to_values
        obj.attrs_ = _attrs
        obj.items_ = sorted(_attrs.keys(), key=lambda x: x)
        return obj

    def __call__(cls, *args, **kw):
        return cls.items_


class Const(metaclass=ConstType):
    pass


# 布尔值是最常用的枚举，所以这里先写一个
class Boolean(Const):
    no = (0, '否')
    yes = (1, '是')


if __name__ == "__main__":
    class Demo(Const):
        # 属性    值    说明
        DEMO1 = (1, "demo1")
        DEMO2 = (2, "demo2")
        DEMO3 = (3, "demo3")

    print(Demo.attrs_)
    print(Demo())
    print(Demo.attrs_)
    print(Demo.values_)
    print(Demo.labels_to_values_)
    print(Demo.labels_)
    print(Demo.DEMO1)
    print(Demo.DEMO2)

