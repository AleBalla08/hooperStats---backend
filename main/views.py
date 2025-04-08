from django.shortcuts import render
from main.serializers import *
from rest_framework import status
from rest_framework.views import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken #type:ignore
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView #type:ignore
from .models import *
from .serializers import *

#Views de Autenticação do usuário:
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.data)
        return Response(serializers.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]



#Views da Sessão:
class CreateSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            name = request.data.get('name')
            if not name:
                return Response({'message': 'Nome é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

            Session.objects.create(name=name)
            return Response({'message': 'Sessão criada com sucesso.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': f'Erro: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class ListSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try: 
            sessions = Session.objects.all()
            serializer = SessionSerializer(sessions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':f'Erro: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        

class CreateExerciseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try: 
            name = request.data.get('name')
            reps = int(request.data.get('reps'))
            Exercise.objects.create(name=name, reps=reps, makes=0, accuracy=0, checked=0)
            return Response({'message':'Exercício criado com sucesso'}, status=status.HTTP_201_CREATED  )
        except Exception as e:
            return Response({'message':f'Erro: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        
    
class ListExercisesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            id_session = request.query_params.get('id_session')
            exercises = Exercise.objects.filter(session_id=id_session).all()
            serializer = ExerciseSerializer(exercises, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':f'Erro: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        
    
class EditExerciseView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):#finaliza o exer
        try:
            id = request.data.get('id')
            makes = int(request.data.get('makes'))
            
            if not id or not makes:
                return Response({'message': 'ID e makes são obrigatórios'}, status=400)
            
            exer = Exercise.objects.filter(id=id).first()
            accuracy = (int(makes) / exer.reps) * 100 if exer.reps > 0 else 0
            exer.makes = makes
            exer.accuracy = accuracy
            exer.checked = 1
            exer.save()
            return Response({'message':'Exercício concluído'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':f'Erro: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        try: 
            id = request.data.get('id')
            exer = Exercise.objects.filter(id=id).first()
            if exer:
                exer.delete()
            return Response({'message':'Exercício removido'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":f"Erro: {e}"}, status=status.HTTP_400_BAD_REQUEST)
    

        



