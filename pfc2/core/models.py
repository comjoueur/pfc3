
from django.db import models
import string
import secrets
from sklearn.cluster import KMeans
import numpy as np

from pfc2.utils import euclidian_distance, get_point_proyection


class Client(models.Model):
    TOKEN_SIZE = 8  # size of client token
    NUM_CLUSTERS = 1  # default of number of clusters that should be formed
    CORRECT_WEIGHT = 3  # weight of correct touches
    INCORRECT_WEIGHT = 1  # weight of incorrect touches
    MINIMAL_INCORRECT_DISTANCE = 10  # minimal distance to assign a button to incorrect touch
    NUM_LAST_TOUCHES = 100  # number of maximal last touches to apply the k means
    ONLY_RELATIVE_BUTTONS = False  # consider all button or only the buttons used
    MAXIMAL_BUTTON_MOVEMENT = 15  # maximal button movement
    BUTTON_GROWING = 1.3 ** 0.5  # button growing ratio
    NUM_BUTTON_GROWING = 2  # num of  buttons to grow
    ADAPTATION_MODE = True  # enable adaptation

    channel_ws = models.CharField(max_length=256)
    token = models.CharField(max_length=TOKEN_SIZE, unique=True)

    @classmethod
    def generate_valid_client_token(cls):
        alphabet = string.digits
        valid_token = False
        token = None
        while not valid_token:
            token = ''.join(secrets.choice(alphabet) for _ in range(cls.TOKEN_SIZE))
            valid_token = not cls.objects.filter(token=token).exists()
        return token

    def get_touches_per_button(self, button_touches, weighted=False):
        if weighted:
            touches = []
            for touch in button_touches:
                touches += [touch.position] * (self.CORRECT_WEIGHT if touch.button else self.INCORRECT_WEIGHT)
            return touches
        return [touch.position for touch in button_touches]

    def get_centroid_per_button(self, button_touches, weighted=False, num_clusters=None):
        clusters = self.NUM_CLUSTERS
        if num_clusters is not None:
            clusters = num_clusters
        touches = self.get_touches_per_button(button_touches, weighted)
        if len(touches) < clusters:
            return None
        array_touches = np.array(touches)
        kmeans = KMeans(n_clusters=clusters, init='k-means++', random_state=0).fit(array_touches)
        return kmeans.cluster_centers_

    def get_centroids_last_touches(self, weighted=False, num_clusters=None):
        touches = self.touches.order_by('-created')[:self.NUM_LAST_TOUCHES]
        touches_button = {}
        client_buttons = self.buttons.all()
        for button in client_buttons:
            touches_button[button.id] = []
        for touch in touches:
            if touch.button:
                touches_button[touch.button.id].append(touch)
        centroids = []
        for button in client_buttons:
            centroid = self.get_centroid_per_button(touches_button[button.id], weighted, num_clusters)
            centroids.append((centroid, button))
        return centroids

    def get_color_last_touches(self, weighted=False):
        touches = self.touches.order_by('-created')[:self.NUM_LAST_TOUCHES]
        touches_button = {}
        client_buttons = self.buttons.all()
        for button in client_buttons:
            touches_button[button.id] = []
        for touch in touches:
            if touch.button:
                touches_button[touch.button.id].append(touch)
        centroids = []
        for button in client_buttons:
            button = Button.objects.filter(id=button.id).first()
            touches, mod_button = self.get_touches_per_button(button, weighted)
            button.color = mod_button.modificated_color
        return centroids

    def get_shade_last_touches(self, weighted=False):
        touches = self.touches.order_by('-created')[:self.NUM_LAST_TOUCHES]
        touches_button = {}
        client_buttons = self.buttons.all()
        for button in client_buttons:
            touches_button[button.id] = []
        for touch in touches:
            if touch.button:
                touches_button[touch.button.id].append(touch)
        centroids = []
        for button in client_buttons:
            button = Button.objects.filter(id=button.id).first()
            touches, mod_button = self.get_touches_per_button(button, weighted)
            button.shade_direction = mod_button.modificated_color
        return centroids

    def get_border_last_touches(self, weighted=False):
        touches = self.touches.order_by('-created')[:self.NUM_LAST_TOUCHES]
        touches_button = {}
        client_buttons = self.buttons.all()
        for button in client_buttons:
            touches_button[button.id] = []
        for touch in touches:
            if touch.button:
                touches_button[touch.button.id].append(touch)
        centroids = []
        for button in client_buttons:
            button = Button.objects.filter(id=button.id).first()
            touches, mod_button = self.get_touches_per_button(button, weighted)
            button.border_size = mod_button.modificated_border
        return centroids

    def get_transparency_last_touches(self, weighted=False):
        touches = self.touches.order_by('-created')[:self.NUM_LAST_TOUCHES]
        touches_button = {}
        client_buttons = self.buttons.all()
        for button in client_buttons:
            touches_button[button.id] = []
        for touch in touches:
            if touch.button:
                touches_button[touch.button.id].append(touch)
        centroids = []
        for button in client_buttons:
            button = Button.objects.filter(id=button.id).first()
            touches, mod_button = self.get_touches_per_button(button, weighted)
            button.transparency = mod_button.modificated_transparency
        return centroids

    def get_centroids_button_touches(self, weighted=False, num_clusters=None):
        centroids = []
        for button in self.buttons.all():
            touches = button.touches.order_by('-created')[:self.NUM_LAST_TOUCHES]
            centroid = self.get_centroid_per_button(touches, weighted, num_clusters)
            centroids.append((centroid, button))
        return centroids

    def get_centroids(self, weighted=False, num_clusters=None):
        if self.ONLY_RELATIVE_BUTTONS:
            return self.get_centroids_last_touches(weighted, num_clusters)
        return self.get_centroids_button_touches(weighted, num_clusters)

    def get_sizes(self):
        touches = self.touches.order_by('-created')[:self.NUM_LAST_TOUCHES]
        if len(touches) > 0:
            touches_button = {}
            client_buttons = self.buttons.all()
            for button in client_buttons:
                touches_button[button.id] = 0
            for touch in touches:
                if touch.button:
                    touches_button[touch.button.id] += 1
            return [w for w in sorted(touches_button, key=touches_button.get, reverse=True)
                    if touches_button[w] > 2][:self.NUM_BUTTON_GROWING]
        return []

    def update_buttons(self):
        centroids = self.get_centroids()
        for centroid, button in centroids:
            if centroid is not None:
                default_center = button.get_default_center()
                button.center = get_point_proyection(default_center, centroid[0], self.MAXIMAL_BUTTON_MOVEMENT)
                button.save()
        button_ids = self.get_sizes()
        if len(button_ids):
            for button in self.buttons.all():
                if button.id in button_ids:
                    button.size = button.DEFAULT_BUTTON_SIZE * self.BUTTON_GROWING
                else:
                    button.size = button.DEFAULT_BUTTON_SIZE
                button.save()

    def get_buttons_positions(self):
        positions = {}
        for button in self.buttons.all():
            positions[button.kind] = {
                'left': button.center[0] - button.size,
                'top': button.center[1] - button.size,
                'height': 2 * button.size,
                'width': 2 * button.size,
            }
        return positions

    def __str__(self):
        return self.token


class Button(models.Model):
    BUTTON_LEFT = 'left'
    BUTTON_UP = 'up'
    BUTTON_RIGHT = 'right'
    BUTTON_DOWN = 'down'
    BUTTON_PAUSE = 'pause'
    BUTTON_START = 'start'
    KIND_BUTTON_CHOICES = [
        (BUTTON_LEFT, 'Left Button'),
        (BUTTON_RIGHT, 'Right Button'),
        (BUTTON_DOWN, 'Down Button'),
        (BUTTON_UP, 'Up Button'),
        (BUTTON_START, 'Start Button'),
        (BUTTON_PAUSE, 'Pause Button'),
    ]
    DEFAULT_POSITION = {
        BUTTON_LEFT: (45, 245),
        BUTTON_UP: (120, 175),
        BUTTON_RIGHT: (195, 245),
        BUTTON_DOWN: (120, 315),
        BUTTON_PAUSE: (585, 175),
        BUTTON_START: (585, 315),
    }
    DEFAULT_BUTTON_SIZE = 35  # Default button circular ratio

    center_x = models.IntegerField(default=0)
    center_y = models.IntegerField(default=0)
    kind = models.CharField(null=True, blank=True, max_length=32, choices=KIND_BUTTON_CHOICES)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='buttons')
    size = models.IntegerField(default=DEFAULT_BUTTON_SIZE)
    encode_shade = models.CharField(max_length=430, default="0_8_15_0.2")
    shade_direction = models.CharField(max_length=128, default="LEFT")
    encode_background_color = models.CharField(max_length=128, default="89_133_234")
    transparency = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    border_size = models.DecimalField(default=1.2, decimal_places=2, max_digits=10)

    @property
    def center(self):
        return self.center_x, self.center_y

    @center.setter
    def center(self, new_center):
        self.center_x = new_center[0]
        self.center_y = new_center[1]

    def get_default_center(self):
        return self.DEFAULT_POSITION[self.kind]

    def __str__(self):
        return '{}, {}, {}'.format(self.center_x, self.center_y, self.kind)


class Touch(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='touches')
    button = models.ForeignKey(Button, on_delete=models.CASCADE, related_name='touches', null=True)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    @property
    def position(self):
        return self.position_x, self.position_y

    @position.setter
    def position(self, new_position):
        self.position_x = new_position[0]
        self.position_y = new_position[1]

    def set_relative_button(self):
        if not self.button:
            for button in self.client.buttons.all():
                distance = button.size + Client.MINIMAL_INCORRECT_DISTANCE
                if euclidian_distance(button.center, self.position) <= distance ** 2:
                    self.button = button

    def __str__(self):
        if self.button:
            return '{}, {}, {}'.format(self.position_x, self.position_y, self.button.kind)
        else:
            return '{}, {}'.format(self.position_x, self.position_y)
