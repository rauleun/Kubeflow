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

![kubectl get pv](./image/kubectl_get_pv.GIF)

![kubectl get pvc](./image/kubectl_get_pvc.GIF)


Pod가 정상적으로 생성되었는지 kubectl 명령어를 통해서 확인합니다.

~~~
$ kubectl get pods -n ai-dept -o wide
~~~

![kubectl describe pod](./image/kubectl_describe_pod.GIF)


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

**(Model을 전송할 때는 model을 포함하고 있는 숫자 형식의 version 폴더에 담아 전송합니다.)**

Model 전송이 완료되면, model을 담고 있는 path를 참조하는 inference service를 생성합니다.

~~~
$ kubectl apply -f kfserving-infer-svc.yaml -n ai-dept
~~~

![kubectl get inferenceservice](./image/kubectl_get_inferenceservice.GIF)


Inference service의 deployment는 canary 등을 적용할 수 있습니다. 
(upgrade 하고 싶은 model의 경로를 spec: canary에 두고, probability를 할당합니다.)

json file 형태로 data를 변환하여 request를 전송합니다.

예시로는 character detection을 할 수 있는 model을 넣어두고, 글귀가 담긴 pkl file을 json 및 png file로 변환하는 .py 코드를 작성하였습니다.

~~~
$ python kfserving_dataload_ocr.py
~~~

생성된 inference service에 input file에 대한 inference를 요청합니다.

~~~
MODEL_NAME=model-ocr-detect
INPUT_PATH=@ocr_det.json
INGRESS_GATEWAY=istio-ingressgateway
CLUSTER_IP=10.96.37.165
SERVICE_HOSTNAME=$(kubectl get inferenceservice -n ai-dept ${MODEL_NAME} -o jsonpath='{.status.default.predictor.host}')
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH > ./ocr_det_output.json
~~~
**model name**은 생성된 inference service의 이름, 

**input path**는 inference를 하고자 하는 input data의 경로, 

**cluster ip**는 cluster 내에서 작동하고 있는 ingress-gateway node-selector의 ip address, 

**service hostname**은 생성된 inference service에 부여된 url을 입력해줍니다.

명령어들을 shell script로 작성하여 curl로 요청을 보낸 뒤, json file로 저장해줍니다.

저장한 json file 다시 png로 변환합니다.

~~~
$ python kfserving_output.py
~~~

**input image (text)**

![input image](./image/ocr_det.png)

**output image (detected heatmap)**

![output image](./image/ocr_det_output.png)

