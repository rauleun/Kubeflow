MODEL_NAME=model-espcn
INPUT_PATH=@data-espcn/0100.json
INGRESS_GATEWAY=istio-ingressgateway
CLUSTER_IP=10.96.184.156
SERVICE_HOSTNAME=$(kubectl get inferenceservice -n kubeflow ${MODEL_NAME} -o jsonpath='{.status.default.predictor.host}')
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH > ./output.json
