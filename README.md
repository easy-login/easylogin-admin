# easylogin-admin

Hướng dẫn deploy easylogin admin.

## Yêu cầu hệ thống

Tương tự project [*easylogin-core*](https://gitlab.com/mirabo/easylogin-core).


## Config MySQL

Tham khảo project [*easylogin-core*](https://gitlab.com/mirabo/easylogin-core), có thể sử dụng chung account MySQL của project trên hoặc tạo account riêng.


## Deploy EasyLogin admin

Clone project từ Gitlab:

```
git clone git@gitlab.com:mirabo/easylogin-admin.git
```

### Configuration

Di chuyển vào trong thư mục chứa project, tạo file *.env* để chứa các biến môi trường (nội dung tham khảo file *.env.test*). Sửa các giá trị config tương ứng với MySQL instance đang được sử dụng:

```
DATABASE_NAME=easylogin
DATABASE_USER=easylogin
DATABASE_PASSWORD=your_secret
DATABASE_HOST=your_mysql_url
DATABASE_PORT=3306

DEBUG=0

```

> Để biết đầy đủ các tham số có thể cấu hình, tham khảo file *SocialPlus/settings.py*


### Build and run

Build Docker image:

```
docker-compose build
```

> Docker-compose đã tự động mount thư mục code vào trong các image nên trừ khi có thay đổi về dependencies (trong file requirements) nếu không thì không cần thiết build lại Docker image mỗi khi thay đổi code.

Nếu là lần đầu tiên khởi tạo project thì cần chạy Django migrate bằng cách chạy lần lượt các lệnh sau:

```
docker-compose run web python manage.py makemigrations loginapp
docker-compose run web python manage.py migrate
```

Start service bằng lệnh sau:

```
docker-compose up -d
```

Gõ lệnh `docker ps`, nếu kết quả có dạng như sau là thành công:

```
CONTAINER ID        IMAGE               COMMAND                 CREATED             STATUS              PORTS                    NAMES
3e1284cbc96f        easyadmin            "sh gunicorn.sh"        3 hours ago         Up 3 hours          0.0.0.0:8000->7000/tcp   easyadmin
```

## Deploy with nginx

Tạo một file với tên là *easyadmin.conf* thư mục conf của Nginx (thông thường ở */etc/nginx/conf.d*) với nội dung như sau (lưu ý thay đổi các **subdomain** và **port** của các service cho đúng nếu bạn không chạy các service ở các port mặc định):

```
upstream admin_server {
    server localhost:8000 fail_timeout=0;
}

server {
    server_name admin.social-login.mirabo.co.jp;
    listen 443 ssl;
    listen [::]:443 ssl;

    location / {
      # checks for static file, if not found proxy to app
      try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header Host $http_host;
      proxy_set_header X-Real-IP $remote_addr;

      # we don't want nginx trying to do something clever with
      # redirects, we set the Host: header above already.
      proxy_redirect off;
      proxy_pass http://admin_server;

      proxy_set_header Connection '';
      proxy_http_version 1.1;
      chunked_transfer_encoding off;
      proxy_buffering off;
      proxy_cache off;
    }
}
```