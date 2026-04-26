extends Node

class_name Player

var speed = 200
var health = 100

func _ready():
	print("Player ready")

func move(direction):
	position += direction * speed

func take_damage(amount):
	health -= amount
	if health <= 0:
		die()

func die():
	queue_free()

var weapon = preload("res://weapons/sword.gd")
