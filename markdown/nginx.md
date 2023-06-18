[TOC]


# 部署
## docker 部署
docker run -d -p 80:80 --name nginx nginx:latest

rewrite 重定向 四个参数：
1. last 中断当前location 不再往下执行，跳出location之后接着往下执行， 如：第9行增加last之后 第十行不再执行，当时
    跳出location之后，第13行会继续执行
2. break 跳出当前location 之后, 剩下的也不会执行
3. redirect url 302临时重定向
4. permanent 301 永久重定向，浏览器会缓存记录 跳转服务器挂了也能重定向成功，(清掉浏览器缓存跳转也会失败)

```commandline
servver {
    listen 80;
    server_name localhost;
    location / {
        rewrite /(.*) http://xx.xx.xx.xx permanent|redirect;
    }
    location /a.html {
        rewrite /a.html /b.html last|break;
        rewrite /b.html /c.html;
    }
    location /b.html {
        return 200 "this is b.html \n";
    }
    location /c.html {
        return 200 "this is c.html \n";
    }
}
```

# location
优先级: 精准匹配(=) > 非正则匹配(^~) > 正则匹配 (~|~*)  正则匹配的优先级相同，谁在上方优先匹配谁

```commandline
location ~* \.jpg {
    return 200 "this is ~* \.jpg \n";
}
location ~ \.(jpg|JPG) {
    return 200 "this is ~ \.(jpg|JPG) \n";
}
location ^~ /img/ {  # 非正则匹配
    return 200 "this is ^~/img/ \n";
}
location = /img/test.jpg {  # 精准匹配
    return 200 "this is = /img/test.jpg"
}
```