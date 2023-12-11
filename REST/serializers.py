from rest_framework import serializers

from REST.models import Message, Friend, MyUser, Group


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = MyUser
        fields = ['firstName', 'lastName', 'username', 'email', 'date_of_birth', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = MyUser(firstName=self.validated_data['firstName'], lastName=self.validated_data['lastName'],
                      username=self.validated_data['username'], email=self.validated_data['email'],
                      date_of_birth=self.validated_data['date_of_birth'])
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password)
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"}, required=True)
    new_password = serializers.CharField(style={"input_type": "password"}, required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError({'current_password': 'Does not match'})
        return value


class GroupDetailSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('id', 'name', 'logo_url', 'user_count')

    def get_user_count(self, obj):
        return obj.users.count()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'logo_url', 'group_site_url', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class PersonSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    number_of_following = serializers.SerializerMethodField()
    number_of_followers = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ('id', 'firstName', 'lastName', 'username', 'email', 'age', 'profile_picture', 'gender', 'latitude',
                  'longitude', 'number_of_following', 'number_of_followers', 'description','groups')

    def get_number_of_following(self, obj):  # Metoda dostaje pojedynczy obiekt który jest serializowany (prefix get_)
        return obj.person.all().count()

    def get_number_of_followers(self, obj):  # Metoda dostaje pojedynczy obiekt który jest serializowany (prefix get_)
        return obj.person_friends.all().count()


class UpdateFriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = '__all__'


class ShowFriendSerializer(serializers.ModelSerializer):
    friend = PersonSerializer()

    class Meta:
        model = Friend
        fields = ('friend',)


class MessageSerializer(serializers.ModelSerializer):
    sender = PersonSerializer(read_only=True)
    receiver = PersonSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'text', 'created_at']


class UpdateMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class UserWithDistanceSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    number_of_following = serializers.SerializerMethodField()
    number_of_followers = serializers.SerializerMethodField()
    distance = serializers.FloatField(required=False)
    online = serializers.BooleanField(required=False)

    class Meta:
        model = MyUser
        fields = ('id', 'firstName', 'lastName', 'username', 'email', 'age', 'profile_picture', 'gender', 'latitude',
                  'longitude', 'number_of_following', 'number_of_followers', 'description', 'distance', 'online',
                  'groups')

    def get_number_of_following(self, obj):  # Metoda dostaje pojedynczy obiekt który jest serializowany (prefix get_)
        return obj.person.all().count()

    def get_number_of_followers(self, obj):  # Metoda dostaje pojedynczy obiekt który jest serializowany (prefix get_)
        return obj.person_friends.all().count()
