from rest_framework import serializers

from REST.models import Message, MyUser, Group, Alert, BlockedUsers


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

    class Meta:
        model = MyUser
        fields = ('id', 'firstName', 'lastName', 'username', 'email', 'age', 'date_of_birth', 'profile_picture',
                  'gender', 'latitude', 'longitude', 'description',
                  'groups')


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
    distance = serializers.FloatField(required=False)
    online = serializers.BooleanField(required=False)

    class Meta:
        model = MyUser
        fields = ('id', 'firstName', 'lastName', 'username', 'email', 'age', 'profile_picture', 'gender', 'latitude',
                  'longitude', 'description', 'distance', 'online',
                  'groups')


class AlertSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)
    user = PersonSerializer(read_only=True)

    class Meta:
        model = Alert
        fields = ['id', 'user', 'title', 'content', 'start_date', 'end_date', 'group', 'style']


class AlertSerializerSave(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'user', 'title', 'content', 'start_date', 'end_date', 'group', 'style']


class BlockedUsersListSerializer(serializers.ModelSerializer):
    blocked_user = PersonSerializer(read_only=True)

    class Meta:
        model = BlockedUsers
        fields = ['id', 'blocked_user']


class BlockedUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedUsers
        fields = '__all__'
