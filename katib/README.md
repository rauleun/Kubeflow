# katib

katib은 hyperparameter tuning을 지원해주는 kubeflow의 module입니다.

autoML 기반의 hyperparameter optimization이 가능합니다.

![katib](https://github.com/rauleun/Kubeflow/blob/master/katib/README-images/katib.png)

---

### 1. model traininig

kfserving과 마찬가지로,image super-resolution model인 ESPCN의 training 과정을 자동화하고 hyperparameter을 최적화해보는 예제를 진행해보겠습니다.

ESPCN model을 학습하는 code가 담긴 image를 docker hub에서 불러와서 container를 생성하고 pod 안에 담습니다.

`(rauleun/ai-kubeflow:ver6)`

pod를 생성하고 내부로 접속하여 학습하는 python file을 실행합니다.

```
$ kubectl apply -f pod-katib.yaml -n kubeflow

$ kubectl exec -it pod-katib -c container-katib -n kubeflow /bin/bash

$ python /home/super_resolution-module_SR_VESPCN/tf2/srcs/trainers/espcn/espcn_trainer_gradient_tape.py
```

gpu에 연결되면 아래처럼 cuda library가 잘 실행되며 training이 시작됩니다.

![gpu-ok](https://github.com/rauleun/Kubeflow/blob/master/katib/README-images/gpu-ok.GIF)

training과 validation 과정을 거쳐 model을 저장하고, 각 training step 마다 PSNR 결과를 보여줍니다.

metric이 잘 도출되는 것까지 확인하면, experiment를 만들어 hyperparameter optimization을 진행합니다.

---

### 2. katib experiment

최적화하고자 하는 hyperparameter에 따라, 최적화하는 방식에 따라 katib experiment yaml file을 작성합니다.

`-objective`

```
$  objective:
$    type: maximize
$    goal: 50
$    objectiveMetricName: PSNR-validation
$  metricsCollectorSpec:
$    collector:
$      kind: StdOut
```

성능 평가를 하는 metric을 정의합니다. metric의 이름과 최적화하는 방향, 목표 수치 등을 입력합니다. 이 때 metric의 이름은 training 과정에서 출력하는 metric의 이름과 정확히 일치해야 합니다.

metric을 수집하는 metric collector은 StdOut collector을 사용합니다.

**(tensorflow summary collector 같은 경우에는, 현재 버전 기준으로 Tensorflow 1에 대해서만 지원합니다. 본 코드는 Tensorflow2로 작성되었기 때문에 사용하지 않았습니다.)**

`-algorithm`

```
$  algorithm:
$    algorithmName: bayesianoptimization
```
optimization algorithm을 정의합니다. 

algorithm의 종류로는 random, gridsearch, **bayesian optimization** 등을 지원합니다.

`-parameters`

```
$  parameters:
$    - name: --learning_rate
$      parameterType: double
$      feasibleSpace:
$        min: "0.001"
$        max: "0.003"
$        step: "0.0001"
$    - name: --batch_size
$      parameterType: int
$      feasibleSpace:
$        min: "16"
$        max: "40"       
```

최적화를 통해 결정할 parameter을 정의합니다.

본 예제에서는 learning rate과 batch size를 최적화하였습니다.

learning rate은 0.001 ~ 0.003 사이의 값 중에서 임의의 실수값을, batch size는 16 ~ 40 사이의 값 중에서 임의의 정수값을 선택하여 최적화했습니다.

`-trial template`

experiment는 suggestion을 통해서 test하고자 하는 parameter 값을 결정합니다.

parameter 값이 결정되고 나면 job이 trial을 병렬적으로 생성하여 결정된 parameter에 대한 validation metric 결과값을 추출합니다.

validation metric 결과값이 목표치에 도달하거나, 사전에 정의한 max trial count의 개수만큼 trial을 진행한다면 experiment가 종료됩니다.

trial template에는 trial에 따라 model을 학습해주는 container을 정의해주고 각 trial마다 자원을 할당해줄 수 있습니다.

또한 command 란에 저장 경로 등의 argument를 추가하여 학습을 진행할 수 있습니다.

---

### 3. graph 

experiment가 종료되면, kubeflow UI를 통해서 graph 형태의 experiment result를 확인할 수 있습니다.

graph에서는 suggestion에서 결정한 parameter values와 그에 대한 metric result를 보여줍니다.

![katib-graph](https://github.com/rauleun/Kubeflow/blob/master/katib/README-images/katib-graph.png?raw=true)

최고의 성능을 보여준 hyperparameter을 결정할 수 있습니다.

각 trial에 대한 결과는 table을 통해서도 확인할 수 있습니다.

![katib-table](https://github.com/rauleun/Kubeflow/blob/master/katib/README-images/katib-table.GIF)



