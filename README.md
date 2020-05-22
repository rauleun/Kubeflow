# Kubeflow
## KFserving 

Kubernetes (version 1.15.3)
cluster - master node 에서 작업하였습니다.

Inference server를 올리기 위해 KFserving module 설치합니다. (version 0.2.0)

~~~
$ kubectl apply -f kfserving.yaml
~~~  

환경분리를 위해 namespace를 생성합니다.

~~~
$ kubectl create namespace ai-dept
~~~ 

Pod를 만들어 내부 container(nginx)에 pretrained model을 load 해야 합니다.

Model을 pod에 mount된 비휘발성의 volume에 저장하기 위해 persistent volume claim을 생성합니다.

Persistent volume claim을 apply 했을 때 Persistent volume이 자동으로 mount 되지 않는 경우에는, 

persistent volume을 먼저 apply 하여 'Ready' 상태의 persistent volume을 생성해줍니다.

~~~
$ kubectl apply -f kfserving-pv-ehs -n ai-dept.yaml
$ kubectl apply -f kfserving-pvc-ehs -n ai-dept.yaml
$ kubectl apply -f kfserving-pod-ehs -n ai-dept.yaml
~~~

Pod가 정상적으로 생성되었는지 kubectl 명령어를 통해서 확인합니다.

~~~
$ kubectl get pods -n ai-dept -o wide
~~~

Pod 내부에 container-ehs라는 이름으로 생성해둔 nginx 기반의 container 내부로 접속해줍니다.

~~~
$ kubectl exec -it kfserving-pod-ehs -n ai-dept --container container-ehs /bin/bash
~~~

Model을 옮기기 위해 ssh 환경을 구축해줍니다.

~~~
(root)# apt-get update
(root)# apt-get install net-tools vim openssh-server
(root)# vi /etc/ssh/sshd_config
~~~

Root로의 원격접속을 가능하게 하기 위해서 PermitRootLogin 부분의 주석을 해제하고 yes로 변경합니다.

~~~
(root)# passwd root
(root)# service ssh start
~~~

container가 생성된 pod에 할당된 ip를 확인하기 위하여 pod 정보를 추출합니다.

~~~
$ kubectl describe pod kfserving-pod-ehs -n ai-dept
~~~

scp를 이용해 model을 container 내부로 전송합니다.

~~~
$ scp -r model_path root@pod_ip:/home/path
~~~

** Model을 전송할 때는 model을 포함하고 있는 숫자 형식의 version 폴더에 담아 전송합니다.




