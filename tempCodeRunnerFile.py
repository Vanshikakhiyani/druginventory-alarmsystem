from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import schedule
import time
import smtplib