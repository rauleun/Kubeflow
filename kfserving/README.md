# KF Serving

kubeflow 기능 중 inference service 생성을 도와주는 KF serving 기능에 대해 소개합니다.

Subpixel convolution layer을 통한 image super-resolution을 수행하는 model 중의 하나인 ESPCN model을 pre-trained 해두었습니다.

model을 담기 위해서 persistent volume claim을 생성해줍니다.

'''
$ kubectl apply -f pvc-espcn.yaml
'''


