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

Persistent volume claim을 apply 했을 때 Persistent volume이 자동으로 mount 되지 않는 경우에는, persistent volume을 먼저 apply 하여 'Ready' 상태의 persistent volume을 생성해줍니다.

~~~
$ kubectl apply -f kfserving-pv-ehs -n ai-dept.yaml
$ kubectl apply -f kfserving-pvc-ehs -n ai-dept.yaml
$ kubectl apply -f kfserving-pod-ehs -n ai-dept.yaml
~~~

