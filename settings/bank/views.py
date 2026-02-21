from rest_framework import views, viewsets, status
from rest_framework.generics import GenericAPIView
import joblib
import os
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from .serializers import RegisterSerializer, LoginSerializer, BankSerializer, UserProfileSerializer
from django.conf import settings

class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })

class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })

class LogoutView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)

model_path = os.path.join(settings.BASE_DIR, 'model (2).pkl')
model = joblib.load(model_path)

scaler_path = os.path.join(settings.BASE_DIR, 'scaler (2).pkl')
scaler = joblib.load(scaler_path)

education_list = ['Bachelor', 'Doctorate', 'High School', 'Master']
home_ownership_list = ['OTHER', 'OWN', 'RENT']
loan_intent_list = ['EDUCATION', 'HOMEIMPROVEMENT', 'MEDICAL', 'PERSONAL', 'VENTURE']

def build_features(data):
    numeric = [
        data['person_age'],
        data['person_income'],
        data['person_emp_exp'],
        data['loan_amnt'],
        data['loan_int_rate'],
        data['loan_percent_income'],
        data['cb_person_cred_hist_length'],
        data['credit_score'],
    ]

    gender = [1 if data['person_gender'] == 'male' else 0]

    education = [1 if data['person_education'] == i else 0 for i in education_list]

    home_ownership = [1 if data['person_home_ownership'] == i else 0 for i in home_ownership_list]

    loan_intent = [1 if data['loan_intent'] == i else 0 for i in loan_intent_list]

    prev_default = [1 if data['previous_loan_defaults_on_file'] == 'Yes' else 0]

    return numeric + gender + education + home_ownership + loan_intent + prev_default

class BankAPIView(views.APIView):

    def post(self, request):
        serializer = BankSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            features = build_features(data)
            scaled_data = scaler.transform([features])

            predict = model.predict(scaled_data)[0]
            prob = model.predict_proba(scaled_data)[0][1]

            bank_data = serializer.save(
                predict=int(predict),
                probability=float(prob)
            )

            return Response(
                {'data': BankSerializer(bank_data).data},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)