# KF Serving

kubeflow 기능 중 inference service 생성을 도와주는 KF serving 기능에 대해 소개합니다.

Subpixel convolution layer을 통한 image super-resolution을 수행하는 model 중의 하나인 **ESPCN model**을 pre-trained 해두었습니다.

### model upload

model을 담기 위한 persistent volume claim을 생성하고, describe 기능을 통해 pvc 생성 정보를 확인해줍니다..

모든 namespace는 **kubeflow**로 통일하겠습니다.

~~~
$ kubectl apply -f pvc-espcn.yaml -n kubeflow

$ kubectl describe pvc pvc-model -n kubeflow
~~~

생성된 pvc를 물고 있는 pod를 생성해줍니다.

~~~
$ kubectl apply -f pod-espcn.yaml -n kubeflow
~~~

pod 생성이 완료되면, local에 저장되어 있는 model을 pod 내에 pvc가 마운트된 경로에 복사합니다.

~~~
$ kubectl cp espcn/ pod-espcn:/hd/models -n kubeflow 
~~~

pod 내부로 들어가서 model이 잘 옮겨졌는지 확인하고, tf serving version 형식에 맞게 model이 담긴 폴더를 변경해줍니다.

(*path/version_number/saved_model.pb* 형태로 저장되어야 합니다.)

~~~
$ kubectl exec -it pod-espcn -c container-espcn -n kubeflow /bin/bash
~~~

### create inference service

model upload가 완료되면, model의 저장 위치를 infservice-espcn.yaml의 storage URI에 입력합니다.

cluster의 pvc가 아닌 google cloud 등에 model이 저장되어 있다면 "gs:" 의 형태로 입력합니다. 

잘 기입되었다면 inference service를 생성해줍니다.

이 때, inference service가 생성되는 namespace의 label에는 

** serving.kubeflow.org = true **

** serving.kubeflow.org/inferenceservice = enabled **
 
등이 필수적으로 포함되어야 하며, 아래와 같은 control plane label은 반드시 제거된 상태여야만 합니다.

** control-plane = kubeflow **

namespace의 label은 아래의 명령어로 확인할 수 있습니다.

~~~
$ kubectl describe namespace kubeflow
~~~

