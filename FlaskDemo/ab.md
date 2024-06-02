
以下服务都使用`ab`来进程压测
`ab -n 1000 -c 100 http://localhost:8000/index`

测试结论:
1. flask自带的原生服务器QPS为 1252
2. gunicorn -w 4 + flask QPS为 1911
3. gunicorn -w 4 + gevent + flask QPS 2567
4. gunicorn -w 8 + gevent + flask QPS 2977
5. nginx -w 4 + gunicorn -w 4 + gevent + flask QPS 2161.47
6. nginx -w 4 + gunicorn -w 4 + flask QPS 1587.91
7. django 原生服务器 QPS 700
8. nginx + django 自带服务器 QPS 816
9. nginx + gunicorn + django QPS 1279
10. nginx -w 4 + gunicorn -w 4 + gevent + django QPS 1800+

## flask 原生服务器
`flask --app server-redis:app run --with-threads`
```
Concurrency Level:      100
Time taken for tests:   0.798 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      176000 bytes
HTML transferred:       4000 bytes
Requests per second:    1252.57 [#/sec] (mean)
Time per request:       79.836 [ms] (mean)
Time per request:       0.798 [ms] (mean, across all concurrent requests)
Transfer rate:          215.28 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.9      0       5
Processing:    14   76  13.1     75     117
Waiting:        1   65  13.1     63     103
Total:         14   77  12.8     75     117
```

## gunicorn
### 默认的sync模式
`gunicorn -w 4 -b 0.0.0.0:8000 server-redis:app`
```
Concurrency Level:      100
Time taken for tests:   0.523 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      156000 bytes
HTML transferred:       4000 bytes
Requests per second:    1911.14 [#/sec] (mean)
Time per request:       52.325 [ms] (mean)
Time per request:       0.523 [ms] (mean, across all concurrent requests)
Transfer rate:          291.15 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.7      0       4
Processing:     1   49  10.6     51      75
Waiting:        1   49  10.6     50      74
Total:          5   50  10.1     51      75
```

### worker-class gevent
`gunicorn -w 4 -b 0.0.0.0:8000 server-redis:app --worker-class gevent`

```
Concurrency Level:      100
Time taken for tests:   0.389 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      156000 bytes
HTML transferred:       4000 bytes
Requests per second:    2567.93 [#/sec] (mean)
Time per request:       38.942 [ms] (mean)
Time per request:       0.389 [ms] (mean, across all concurrent requests)
Transfer rate:          391.21 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.8      0       5
Processing:    13   36  13.8     35      80
Waiting:        9   35  13.8     35      79
Total:         14   36  14.0     36      81
```

### 增加一倍worker = 8
`gunicorn -w 8 -b 0.0.0.0:8000 server-redis:app --worker-class gevent` 
```
Concurrency Level:      100
Time taken for tests:   0.336 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      156000 bytes
HTML transferred:       4000 bytes
Requests per second:    2977.56 [#/sec] (mean)
Time per request:       33.585 [ms] (mean)
Time per request:       0.336 [ms] (mean, across all concurrent requests)
Transfer rate:          453.61 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.1      0       6
Processing:     7   30  11.4     28      55
Waiting:        6   30  11.4     27      55
Total:          7   31  11.6     28      57
```

## nginx + gunicorn
`gunicorn -w 4 -b 127.0.0.1:5000 server-redis:app --worker-class gevent`
```
Concurrency Level:      100
Time taken for tests:   0.462 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      161000 bytes
HTML transferred:       5000 bytes
Requests per second:    2166.15 [#/sec] (mean)
Time per request:       46.165 [ms] (mean)
Time per request:       0.462 [ms] (mean, across all concurrent requests)
Transfer rate:          340.58 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.7      0       4
Processing:     5   44  12.5     44      86
Waiting:        2   44  12.4     44      86
Total:          6   44  12.4     45      86
```

## django
`python manage.py runserver 127.0.0.0:5000`
```
Concurrency Level:      100
Time taken for tests:   1.225 seconds
Complete requests:      1000
Failed requests:        362
   (Connect: 0, Receive: 0, Length: 362, Exceptions: 0)
Non-2xx responses:      362
Total transferred:      458546 bytes
HTML transferred:       188208 bytes
Requests per second:    816.38 [#/sec] (mean)
Time per request:       122.492 [ms] (mean)
Time per request:       1.225 [ms] (mean, across all concurrent requests)
Transfer rate:          365.57 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.0      0       4
Processing:     0   87 153.1     24    1122
Waiting:        0   87 153.1     24    1122
Total:          0   88 153.0     25    1124
```

## gunicorn + django 
`gunicorn -w 4 -b 127.0.0.1:5000 wsgi`

```
Concurrency Level:      100
Time taken for tests:   0.781 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      338000 bytes
HTML transferred:       13000 bytes
Requests per second:    1279.80 [#/sec] (mean)
Time per request:       78.138 [ms] (mean)
Time per request:       0.781 [ms] (mean, across all concurrent requests)
Transfer rate:          422.43 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.8      0       5
Processing:     7   73  13.6     73      92
Waiting:        2   73  13.7     73      92
Total:          7   73  13.2     74      92

Percentage of the requests served within a certain time (ms)
  50%     74
  66%     83
  75%     84
  80%     84
  90%     87
  95%     89
  98%     91
  99%     91
 100%     92 (longest request)
```

## gunicorn gevent django
`gunicorn -w 4 -b 127.0.0.1:5000 wsgi --worker-class gevent`
```
Concurrency Level:      100
Time taken for tests:   0.548 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      338000 bytes
HTML transferred:       13000 bytes
Requests per second:    1823.29 [#/sec] (mean)
Time per request:       54.846 [ms] (mean)
Time per request:       0.548 [ms] (mean, across all concurrent requests)
Transfer rate:          601.83 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.7      0       4
Processing:     6   51  10.8     51      85
Waiting:        2   51  10.8     51      85
Total:          6   52  10.4     52      86

Percentage of the requests served within a certain time (ms)
  50%     52
  66%     54
  75%     56
  80%     57
  90%     64
  95%     71
  98%     79
  99%     82
 100%     86 (longest request)
```