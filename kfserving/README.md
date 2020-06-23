# KF Serving

kubeflow 기능 중 inference service 생성을 도와주는 KF serving 기능에 대해 소개합니다.

Subpixel convolution layer을 통한 image super-resolution을 수행하는 model 중의 하나인 **ESPCN model**을 pre-trained 해두었습니다.

![kubeflow](https://www.kubeflow.org/docs/components/serving/kfserving.png)

---


### 1. model upload

model을 담기 위한 persistent volume claim을 생성하고, describe 기능을 통해 pvc 생성 정보를 확인해줍니다..

모든 namespace는 **kubeflow**로 통일하겠습니다.

~~~
$ kubectl apply -f pvc-espcn.yaml -n kubeflow

$ kubectl describe pvc pvc-model -n kubeflow
~~~

![describe_pvc](https://github.com/rauleun/Kubeflow/blob/master/kfserving/data/README_images/describe-pvc.GIF)

생성된 pvc를 물고 있는 pod를 생성해줍니다. 

(pod를 생성하는 yaml 파일에 생성한 pvc 정보를 입력하고, mount 경로를 입력해줍니다.)

~~~
$ kubectl apply -f pod-espcn.yaml -n kubeflow
~~~

pod 생성이 완료되면, local에 저장되어 있는 model을 pod 내에 pvc가 마운트된 경로에 복사합니다.

~~~
$ kubectl cp espcn/ pod-espcn:/hd/models -n kubeflow 
~~~

pod 내부로 들어가서 model이 잘 옮겨졌는지 확인하고, tf serving의 version 형식에 맞게 model이 담긴 폴더를 변경해줍니다.

(*path/version_number/saved_model.pb* 형태로 저장되어야 합니다.)

~~~
$ kubectl exec -it pod-espcn -c container-espcn -n kubeflow /bin/bash
~~~

---

### 2. create inference service

model upload가 완료되면, model의 저장 위치를 infservice-espcn.yaml의 storage URI에 입력합니다.

cluster의 pvc가 아닌 google cloud 등에 model이 저장되어 있다면 "gs:" 의 형태로 입력합니다. 

model 위치가 잘 입력되었다면 inference service를 생성해줍니다.

이 때, inference service가 생성되는 namespace의 label에는 

`serving.kubeflow.org = true`

`serving.kubeflow.org/inferenceservice = enabled`
 
등이 필수적으로 포함되어야 하며, 아래와 같은 control plane label은 반드시 제거된 상태여야만 합니다.

`control-plane = kubeflow`

만약 control-plane label이 제거되지 않은 상태라면, storage initializer가 정상적으로 생성되지 않아 inference service가 model path를 파악하지 못하는 문제가 발생합니다. (Filesystem access error)

namespace의 label은 아래의 명령어로 확인할 수 있습니다.

~~~
$ kubectl describe namespace kubeflow
~~~

![describe_namespace](https://github.com/rauleun/Kubeflow/blob/master/kfserving/data/README_images/describe-namespace.GIF)

inference service를 생성한 후 traffic이 잘 전송되고 있다면, URL이 생성되고 READY 란에 `TRUE`가 표기됩니다.

~~~
$ kubectl apply -f infservice-espcn -n kubeflow
$ kubectl get inferenceservice -A
~~~

![get_infservice](https://github.com/rauleun/Kubeflow/blob/master/kfserving/data/README_images/get-infservice.GIF)

---

### 3. request inference

kfserving inference service는 json 형태의 데이터만을 처리할 수 있습니다.

따라서 inference 하고자 하는 image file (png)를 json으로 변환해주어야 합니다.

```
$ python data-input.py
```

`input path`, `ingress gateway`, `cluster IP`, `service hostname` 등을 지정해주고 inference service에 request를 전송합니다.

```
MODEL_NAME=model-espcn
INPUT_PATH=@data-espcn/0100.json
INGRESS_GATEWAY=istio-ingressgateway
CLUSTER_IP=10.96.184.156
SERVICE_HOSTNAME=$(kubectl get inferenceservice -n kubeflow ${MODEL_NAME} -o jsonpath='{.status.default.predictor.host}')
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH > ./output.json
```

inference service의 output은 json file로 저장합니다.

x-envoy-upstream-service-time에 추론에 소요된 시간이 표시됩니다.

json 형태로 저장된 output을 image file (png)로 다시 변환합니다.

```
python data-output.py
```



