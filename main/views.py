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
    serializer_class = RegisterSerializer
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
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

            Session.objects.create(name=name, user=request.user)
            return Response({'message': 'Sessão criada com sucesso.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': f'Erro: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class ListSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try: 
            sessions = Session.objects.filter(user=request.user).all()
            serializer = SessionSerializer(sessions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':f'Erro: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        
class EditSessionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        try:
            id = request.data.get('id')
            name = request.data.get('name')
            if not name or not id:
                return Response({'message':'Parâmetros incorretos.'}, status=status.HTTP_400_BAD_REQUEST)
            session = Session.objects.filter(id=id).first()
            session.name = name
            session.save()
            return Response({'message':'Edição realizada.'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'message':e},status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        try:
            id = request.data.get('id')
            if not id:
                return Response({'message':'ID obrigatorio'}, status=400)
            session = Session.objects.filter(id=id).first()
            session.delete()
            return Response({'message':'Removido com sucesso'}, status=200)
        except Exception as e:
            return Response({'message':e}, status=400)

    

    

        

class CreateExerciseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try: 
            name = request.data.get('name')
            reps = int(request.data.get('reps'))
            session_id = request.data.get('session_id')
            session = Session.objects.filter(id=session_id).first()
            
            Exercise.objects.create(name=name, reps=reps, makes=0, accuracy=0, checked=0, session=session)
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

    def patch(self, request): #finaliza o exer
        try:
            id = request.data.get('id')
            makes = int(request.data.get('makes'))
            
            if not id or makes is None:
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
    
    def put(self, request):
        try:
            id = request.data.get('id')
            name = request.data.get('name')
            reps = request.data.get('reps', 0)

            if not id or name == '':
                return Response({'message':'Parametros Invalidos.'}, status=status.HTTP_400_BAD_REQUEST)
            
            exer = Exercise.objects.filter(id=id).first()
            exer.name = name
            exer.reps = reps
            exer.makes = 0
            exer.accuracy = 0
            exer.save()
            return Response({'message':'Sucesso.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message':e}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        try: 
            id = request.data.get('id')
            exer = Exercise.objects.filter(id=id).first()
            if exer:
                exer.delete()
            return Response({'message':'Exercício removido'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":f"Erro: {e}"}, status=status.HTTP_400_BAD_REQUEST)


#tasks views

class CreateTask(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            user = request.user
            name = request.data.get('name')
            checked = 0
            if name == "":
                return Response({'message':'O nome é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
            Tasks.objects.create(
                user=user,
                name = name,
                checked = checked
            )
            return Response({"message":"Criado com sucesso."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':e}, status=status.HTTP_400_BAD_REQUEST)

class EditaTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            id = request.data.get('id')
            checked = request.data.get('checked', 0)

            if not id:
                return Response({'message': 'O ID é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
            
            task = Tasks.objects.filter(id=id).first()
            if not task:
                return Response({'message': 'Tarefa não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
            
            task.checked = checked
            task.save()
            return Response({'message': 'Salvo com sucesso'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Erro: {e}'}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        try:
            id = request.data.get('id')
            if not id:
                return Response({'message': 'ID não encontrado.'}, status=status.HTTP_401_UNAUTHORIZED)
            task = Tasks.objects.filter(id=id).first()
            task.delete()
            return Response({'message':'Removido com sucesso.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': e}, status=status.HTTP_400_BAD_REQUEST)
            

    
    def put(self, request):
        id = request.data.get('id')

        if not id:
                return Response({'message':'o ID é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        task = Tasks.objects.filter(id=id).first()
        novo_nome = request.data.get('novo_nome')

        if novo_nome != '':
            task.name = novo_nome
            task.checked = 0
            task.save()
        else:
            return Response({'message':'O nome não pode ser vazio'}, status=status.HTTP_400_BAD_REQUEST)

class ListTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            tasks = Tasks.objects.filter(user=request.user).all()
            serializer = TasksSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':e}, status=status.HTTP_200_OK)

        

    
    

        
    

        



