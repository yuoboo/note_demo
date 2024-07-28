# CICD

## 怎么发布版本

### 开发环境

- 完成提交代码并合并相关的提交至 *dev* 分支 
- 切换至 *dev* 分支
- 执行 ./release.sh -v 版本号，如1.0.0

> release.sh 做了什么：
> 创建git的tag，格式如：env-ver-sha (eg. dev-1.0.1-a3dab58e)
> 推送git的tag至远端，触发gitlab-ci
> gitlab-ci完成成功后，触发jenkins-cd部署

### 测试环境

- 完成提交代码并合并相关的提交至 *test* 分支 
- 切换至 *test* 分支
- 执行 ./release.sh -v 版本号，如1.0.0

> release.sh 做了什么：
> 创建git的tag，格式如：env-ver-sha (eg. test-1.0.1-a3dab58e)
> 推送git的tag至远端，触发gitlab-ci
> gitlab-ci完成成功后，运维或者相关负责部署的人员，手工执行jenkins-cd部署

### 正式环境

- 完成提交代码并合并相关的提交至 *master* 分支 
- 切换至 *master* 分支
- 执行 ./release.sh -v 版本号，如1.0.0

> release.sh 做了什么：
> 创建git的tag，格式如：env-ver-sha (eg. pd-1.0.1-a3dab58e)
> 推送git的tag至远端，触发gitlab-ci
> gitlab-ci完成成功后，运维或者相关负责部署的人员，手工执行jenkins-cd部署


## CI yml

```yml
stages:
  - build
  - auto_cd

build:
  stage: build
  script:
    - dm_ci -f Dockerfile -n ${CI_PROJECT_NAME}
  tags:
    - java-ci-runner
  only:
    - tags

auto_cd:
  stage: auto_cd
  variables:
    JENKINS_URL: "http://jenkins.dianmi365.com"
    JENKINS_JOB_VIEW_URL: "view/%E6%94%AF%E6%92%91%E6%9C%8D%E5%8A%A1/job/%E6%8A%A5%E5%90%8D%E6%9C%8D%E5%8A%A1%E4%B8%9A%E5%8A%A1%E7%B3%BB%E7%BB%9F-eebo.ehr.signups/job/D_eebo.ehr.signups"
  script:
    - echo "Hi CD, AUTO DEPLOY!"
    - http_code=`curl -o /dev/null -s -w %{http_code} -I -u cd:11f847d72f04e593deb22ac5a67e39a676 -X POST --url "${JENKINS_URL}/${JENKINS_JOB_VIEW_URL}/buildWithParameters?token=${CI_PROJECT_NAME}&RELEASE_VERSION_TAG=${CI_COMMIT_TAG}"`; if [ "u${http_code}" != "u201" ]; then exit 1; fi
  rules:
    - if: '$CI_COMMIT_TAG =~ /^dev.*$/'
      when: on_success
  tags:
    - java-ci-runner
```

其中 *JENKINS_JOB_VIEW_URL* 为 http://jenkins.dianmi365.com/ 平台上这个任务的的远程触发部署任务的地址。

> 当前只有开发环境 CI 到 CD 是自动触发的



## PROJECT.DAT 与 docker-compose.yml文件的说明

> 这个新一代的CICD的标准，CICD将围绕这个展开后续的一系列优化


```bash
# 单项目单服务例子：
#   假定项目仓库名称： eebo.ehr.demo
#     只有一个服务(API服务)： eebo.ehr.demo
./PROJECT.DAT 文件内容
# eebo.ehr.demo,Dockerfile,eebo.ehr.demo.CD_PROJECT_ENV.yml


# 单项目多服务例子：
#   假定项目仓库名称： eebo.ehr.demo
#     一个服务(API服务)： eebo.ehr.demo
#     另一个服务(worker服务)： eebo.ehr.demo.worker
./PROJECT.DAT 文件内容
# eebo.ehr.demo,Dockerfile,eebo.ehr.demo.CD_PROJECT_ENV.yml
# eebo.ehr.demo.worker,Dockerfile,eebo.ehr.demo.worker.CD_PROJECT_ENV.yml

```

> docker-compose.yml 文件名称以项目的服务名称+运行环境命名为 *基本规则* 


## CD

新的CD：http://jenkins.dianmi365.com/


### CD 任务的说明

举例子说明::

```bash
# ----------------------------------------------------------------------------------------------------------------
# jenkins 任务配置：
#       Usage: /usr/local/bin/dm_cd [ -p <CD_PROJECT_NAME> ] [ -s <CD_PROJECT_SVC_NAME> ] [ -t <RELEASE_TAG_VERSION> ] [ -e <dev|test|pd|local> ]
#       example: /usr/local/bin/dm_cd -p "dm.bp.messgae" -s "dm.bp.messgae" -t "dev-1.0.0-abcdefgh" -e "dev"
#
# jenkins 任务例子：
#
#   单项目单服务例子：
#       jenkins任务一： 消息服务-dm.bp.message / D_dm.bp.message
#           配置：/usr/local/bin/dm_cd -p "dm.bp.messgae" -s "dm.bp.messgae" -t "dev-1.0.0-abcdefgh" -e "dev"
#
#   单项目多服务例子：
#       jenkins任务一： 消息服务-dm.bp.message / D_dm.bp.message
#           配置：/usr/local/bin/dm_cd -p "dm.bp.messgae" -s "dm.bp.messgae" -t "dev-1.0.0-abcdefgh" -e "dev"
#       jenkins任务二： 消息服务-dm.bp.message / D_dm.bp.message.celery
#           配置：/usr/local/bin/dm_cd -p "dm.bp.messgae" -s "dm.bp.messgae.celery" -t "dev-1.0.0-abcdefgh" -e "dev"
# ----------------------------------------------------------------------------------------------------------------
```


# CICD完整协议内容

```bash
# ----------------------------------------------------------------------------------------------------------------
# ftp树规则
#       /FTP服务器/Packages/
#               项目名称=${CD_PROJECT_NAME}/  --- eg: dm.bp.message | eebo.ehr.ucenter | ...
#                       项目环境=${CD_PROJECT_ENV}/   --- eg: local | dev | test | pd
#                               项目包文件=${CD_PROJECT_NAME}-${CD_PROJECT_ENV}-${CD_PROJECT_VERSION}-${CD_PROJECT_COMMIT_SHA}.tar.gz  --- eg: dm.bp.message-dev-0.0.4-f99f2c04.tar.gz | dm.bp.message-dev-0.0.5-f99f2c0g.tar.gz
#
#       如 /FTP服务器/Packages/dm.bp.message/dev/dm.bp.message-dev-0.0.4-f99f2c04.tar.gz
# 其中项目包文件=${CD_PROJECT_NAME}-${CD_PROJECT_ENV}-${CD_PROJECT_VERSION}-${CD_PROJECT_COMMIT_SHA}.tar.gz
# 文件树规则
#       ${CD_PROJECT_NAME}-${CD_PROJECT_ENV}-${CD_PROJECT_VERSION}-${CD_PROJECT_COMMIT_SHA}
#                   ${CD_PROJECT_SVC_NAME}.${CD_PROJECT_ENV}.yml
#
#       如 /FTP服务器/Packages/dm.bp.message/dev/dm.bp.message-dev-0.0.4-f99f2c04.tar.gz 解压后目录 dm.bp.message-dev-0.0.4-f99f2c04
#       单项目单服务的目录内部文件 CD_PROJECT_NAME=dm.bp.message CD_PROJECT_SVC_NAME=dm.bp.message
#                   dm.bp.message.dev.yml
#                   dm.bp.message.test.yml
#                   dm.bp.message.pd.yml
#       单项目多服务的目录内部文件 CD_PROJECT_NAME=dm.bp.message CD_PROJECT_SVC_NAME=dm.bp.message ｜ CD_PROJECT_SVC_NAME=dm.bp.message.celery
#                   dm.bp.message.dev.yml
#                   dm.bp.message.test.yml
#                   dm.bp.message.pd.yml
#                   dm.bp.message.celery.dev.yml
#                   dm.bp.message.celery.test.yml
#                   dm.bp.message.celery.pd.yml
# ----------------------------------------------------------------------------------------------------------------
# jenkins 任务配置：
#       Usage: /usr/local/bin/dm_cd [ -p <CD_PROJECT_NAME> ] [ -s <CD_PROJECT_SVC_NAME> ] [ -t <RELEASE_TAG_VERSION> ] [ -e <dev|test|pd|local> ]
#       example: /usr/local/bin/dm_cd -p "dm.bp.messgae" -s "dm.bp.messgae" -t "dev-1.0.0-abcdefgh" -e "dev"
#
# jenkins 任务例子：
#
#   单项目单服务例子：
#       jenkins任务一： 消息服务-dm.bp.message / D_dm.bp.message
#           配置：/usr/local/bin/dm_cd -p "dm.bp.messgae" -s "dm.bp.messgae" -t "dev-1.0.0-abcdefgh" -e "dev"
#
#   单项目多服务例子：
#       jenkins任务一： 消息服务-dm.bp.message / D_dm.bp.message
#           配置：/usr/local/bin/dm_cd -p "dm.bp.messgae" -s "dm.bp.messgae" -t "dev-1.0.0-abcdefgh" -e "dev"
#       jenkins任务二： 消息服务-dm.bp.message / D_dm.bp.message.celery
#           配置：/usr/local/bin/dm_cd -p "dm.bp.messgae" -s "dm.bp.messgae.celery" -t "dev-1.0.0-abcdefgh" -e "dev"
# ----------------------------------------------------------------------------------------------------------------
# 部署目录结构（中控式）（主机式）
# 单项目单服务例子：
#   /data/wwwROOT/dm.bp.message/METAFILE
#
#   ${CD_ROOT}/${CD_PROJECT_SVC_NAME}-${CD_PROJECT_ENV}-${CD_PROJECT_VERSION}-${CD_PROJECT_COMMIT_SHA}/${CD_PROJECT_SVC_NAME}.${CD_PROJECT_ENV}.yml
#       /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.4-f99f2c04/
#       /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.4-f99f2c04/dm.bp.message.dev.yml
#       /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.4-f99f2c04/dm.bp.message.test.yml
#       /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.4-f99f2c04/dm.bp.message.pd.yml
#       /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.5-f99f2c0c/
#       /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.5-f99f2c0c/dm.bp.message.dev.yml
#       /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.5-f99f2c0c/...
#       /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.6-f99f2c0g/
#       /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.6-f99f2c0g/dm.bp.message.dev.yml
#       /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.6-f99f2c0g/...
#
# 单项目多服务例子：
#   /data/wwwROOT/dm.bp.message/METAFILE
#
#   ${CD_ROOT}/${CD_PROJECT_SVC_NAME}-${CD_PROJECT_ENV}-${CD_PROJECT_VERSION}-${CD_PROJECT_COMMIT_SHA}/${CD_PROJECT_SVC_NAME}.${CD_PROJECT_ENV}.yml
#   /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.4-f99f2c04/
#   /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.4-f99f2c04/dm.bp.message.dev.yml
#   /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.4-f99f2c04/dm.bp.message.test.yml
#   /data/wwwROOT/dm.bp.message/dm.bp.message-dev-0.0.4-f99f2c04/dm.bp.message.pd.yml
#
#   ${CD_ROOT}/${CD_PROJECT_SVC_NAME}-${CD_PROJECT_ENV}-${CD_PROJECT_VERSION}-${CD_PROJECT_COMMIT_SHA}/${CD_PROJECT_SVC_NAME}.${CD_PROJECT_ENV}.yml
#   /data/wwwROOT/dm.bp.message/dm.bp.message.celery-dev-0.0.4-f99f2c04/
#   /data/wwwROOT/dm.bp.message/dm.bp.message.celery-dev-0.0.4-f99f2c04/dm.bp.message.dev.yml
#   /data/wwwROOT/dm.bp.message/dm.bp.message.celery-dev-0.0.4-f99f2c04/dm.bp.message.test.yml
#   /data/wwwROOT/dm.bp.message/dm.bp.message.celery-dev-0.0.4-f99f2c04/dm.bp.message.pd.yml
# ----------------------------------------------------------------------------------------------------------------
# 自动CI-CD：
#   JENKINS_URL/view/<jenkins 任务地址标记>/job/D_<项目服务名称>/buildWithParameters?token=XXXTOKEN&RELEASE_VERSION_TAG=<RELEASE_VERSION_TAG>
# 手动挡CI-CD：
#   buildWithParameters --- 输入框填写<包名称>
# ----------------------------------------------------------------------------------------------------------------
# METAFILE文件例子
#   /data/wwwROOT/dm.bp.message/METAFILE
#     2021-06-21 15:00:00 deploy
#       CD_PROJECT_NAME=eebo.ehr.demo
#       CD_PROJECT_ENV=dev
#       CD_PROJECT_VERSION=1.0.0
#       CD_PROJECT_SVC_NAME=......
#       CD_PROJECT_HOME=......
#       CD_PROJECT_PACKAGE_URL=......
#
#     2021-06-21 15:00:00 deploy
#       CD_PROJECT_NAME=eebo.ehr.demo
#       CD_PROJECT_ENV=dev
#       CD_PROJECT_VERSION=1.0.0
#       CD_PROJECT_SVC_NAME=......
#       CD_PROJECT_HOME=......
#       CD_PROJECT_PACKAGE_URL=......#
# ----------------------------------------------------------------------------------------------------------------
```