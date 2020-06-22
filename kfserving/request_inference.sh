MODEL_NAME=model-ocr-detect
INPUT_PATH=@ocr_det.json
INGRESS_GATEWAY=istio-ingressgateway
CLUSTER_IP=10.96.37.165
#SERVICE_HOSTNAME=$(kubectl get inferenceservice -n ai-dept ${MODEL_NAME} -o jsonpath='{.status.default.predictor.host}')
SERVICE_HOSTNAME=model-ocr-detect-predictor-default.ai-dept.example.com
curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH > ./ocr_det_output.json

