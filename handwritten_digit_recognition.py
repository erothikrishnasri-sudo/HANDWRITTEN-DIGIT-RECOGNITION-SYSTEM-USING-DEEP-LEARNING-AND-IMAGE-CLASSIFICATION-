"""
Handwritten Digit Recognition System Using Deep Learning and Image Classification
Implements CNN-based digit recognition with MNIST-like dataset
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Dropout
from tensorflow.keras.optimizers import Adam
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# ============================================================================
# 1. LOAD AND EXPLORE DATASET
# ============================================================================

def load_digit_dataset():
    """Load the sklearn digits dataset (8x8 pixel images of digits 0-9)"""
    digits = load_digits()
    X = digits.data
    y = digits.target
    
    print("=" * 80)
    print("HANDWRITTEN DIGIT RECOGNITION SYSTEM - DATASET OVERVIEW")
    print("=" * 80)
    print(f"\nTotal Samples: {len(X)}")
    print(f"Image Dimensions: 8x8 pixels")
    print(f"Number of Classes: 10 (digits 0-9)")
    print(f"Total Features: {X.shape[1]}")
    print(f"Feature Range: {X.min():.2f} to {X.max():.2f}")
    
    print("\nClass Distribution:")
    unique, counts = np.unique(y, return_counts=True)
    for digit, count in zip(unique, counts):
        print(f"  Digit {digit}: {count} samples ({count/len(y)*100:.1f}%)")
    
    return X, y, digits

# ============================================================================
# 2. DATA PREPROCESSING
# ============================================================================

def preprocess_data(X, y):
    """Preprocess the digit dataset"""
    # Normalize pixel values to 0-1 range
    X_normalized = X / 16.0
    
    # Reshape for CNN (add channel dimension)
    X_reshaped = X_normalized.reshape(-1, 8, 8, 1)
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X_reshaped, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("\n" + "=" * 80)
    print("DATA PREPROCESSING SUMMARY")
    print("=" * 80)
    print(f"Training set size: {len(X_train)} samples")
    print(f"Test set size: {len(X_test)} samples")
    print(f"Input shape: {X_train.shape}")
    print(f"Normalized pixel range: {X_train.min():.4f} to {X_train.max():.4f}")
    
    return X_train, X_test, y_train, y_test

# ============================================================================
# 3. VISUALIZATION FUNCTIONS
# ============================================================================

def visualize_sample_digits(digits):
    """Visualize sample handwritten digits from the dataset"""
    fig, axes = plt.subplots(2, 5, figsize=(12, 6))
    fig.suptitle('Sample Handwritten Digits (0-9)', fontsize=14, fontweight='bold')
    
    for idx, ax in enumerate(axes.flat):
        # Get one sample for each digit
        digit_indices = np.where(digits.target == idx)[0]
        sample_idx = digit_indices[0]
        
        image = digits.data[sample_idx].reshape(8, 8)
        ax.imshow(image, cmap='gray')
        ax.set_title(f'Digit: {idx}', fontweight='bold')
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/sample_digits.png', dpi=300, bbox_inches='tight')
    print("✓ Sample digits visualization saved")
    plt.close()

def visualize_digit_distribution(y):
    """Visualize the distribution of digits in the dataset"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    unique, counts = np.unique(y, return_counts=True)
    
    # Bar chart
    colors = plt.cm.Set3(np.linspace(0, 1, 10))
    ax1.bar(unique, counts, color=colors, edgecolor='black', alpha=0.8)
    ax1.set_title('Distribution of Digits in Dataset', fontweight='bold', fontsize=12)
    ax1.set_xlabel('Digit')
    ax1.set_ylabel('Count')
    ax1.grid(axis='y', alpha=0.3)
    
    # Pie chart
    ax2.pie(counts, labels=unique, autopct='%1.1f%%', colors=colors, startangle=90)
    ax2.set_title('Digit Percentage Distribution', fontweight='bold', fontsize=12)
    
    plt.suptitle('Dataset Class Distribution', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/digit_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Digit distribution visualization saved")
    plt.close()

def visualize_pixel_intensity(X, y):
    """Visualize pixel intensity statistics by digit"""
    fig, axes = plt.subplots(2, 5, figsize=(14, 8))
    fig.suptitle('Pixel Intensity Distribution by Digit', fontsize=14, fontweight='bold')
    
    for digit in range(10):
        ax = axes[digit // 5, digit % 5]
        digit_pixels = X[y == digit].flatten()
        ax.hist(digit_pixels, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
        ax.set_title(f'Digit {digit}', fontweight='bold')
        ax.set_xlabel('Pixel Intensity')
        ax.set_ylabel('Frequency')
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/pixel_intensity.png', dpi=300, bbox_inches='tight')
    print("✓ Pixel intensity visualization saved")
    plt.close()

def visualize_training_history(history):
    """Visualize model training history"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Accuracy
    ax1.plot(history.history['accuracy'], label='Training Accuracy', linewidth=2)
    ax1.plot(history.history['val_accuracy'], label='Validation Accuracy', linewidth=2)
    ax1.set_title('Model Accuracy Over Epochs', fontweight='bold', fontsize=12)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Loss
    ax2.plot(history.history['loss'], label='Training Loss', linewidth=2)
    ax2.plot(history.history['val_loss'], label='Validation Loss', linewidth=2)
    ax2.set_title('Model Loss Over Epochs', fontweight='bold', fontsize=12)
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    plt.suptitle('Training History', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/training_history.png', dpi=300, bbox_inches='tight')
    print("✓ Training history visualization saved")
    plt.close()

def visualize_confusion_matrix(y_true, y_pred):
    """Visualize confusion matrix"""
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                xticklabels=range(10), yticklabels=range(10))
    plt.title('Confusion Matrix - Handwritten Digit Recognition', fontweight='bold', fontsize=12)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/confusion_matrix.png', dpi=300, bbox_inches='tight')
    print("✓ Confusion matrix visualization saved")
    plt.close()

def visualize_model_performance(results):
    """Visualize model performance metrics"""
    models = list(results.keys())
    accuracy = [results[m]['Accuracy'] for m in models]
    precision = [results[m]['Precision'] for m in models]
    recall = [results[m]['Recall'] for m in models]
    f1 = [results[m]['F1-Score'] for m in models]
    
    x = np.arange(len(models))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.bar(x - 1.5*width, accuracy, width, label='Accuracy', alpha=0.8, edgecolor='black')
    ax.bar(x - 0.5*width, precision, width, label='Precision', alpha=0.8, edgecolor='black')
    ax.bar(x + 0.5*width, recall, width, label='Recall', alpha=0.8, edgecolor='black')
    ax.bar(x + 1.5*width, f1, width, label='F1-Score', alpha=0.8, edgecolor='black')
    
    ax.set_title('Model Performance Comparison', fontweight='bold', fontsize=14)
    ax.set_ylabel('Score')
    ax.set_ylim([0, 1.1])
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/model_performance.png', dpi=300, bbox_inches='tight')
    print("✓ Model performance visualization saved")
    plt.close()

def visualize_prediction_examples(X_test, y_test, y_pred, num_examples=20):
    """Visualize prediction examples"""
    fig, axes = plt.subplots(4, 5, figsize=(14, 10))
    fig.suptitle('Prediction Examples (Green=Correct, Red=Incorrect)', fontsize=14, fontweight='bold')
    
    for idx, ax in enumerate(axes.flat):
        if idx < num_examples:
            image = X_test[idx].reshape(8, 8)
            true_label = y_test[idx]
            pred_label = y_pred[idx]
            
            ax.imshow(image, cmap='gray')
            
            # Color based on correctness
            color = 'green' if true_label == pred_label else 'red'
            ax.set_title(f'True: {true_label}, Pred: {pred_label}', 
                        fontweight='bold', color=color)
            ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/prediction_examples.png', dpi=300, bbox_inches='tight')
    print("✓ Prediction examples visualization saved")
    plt.close()

# ============================================================================
# 4. MODEL BUILDING AND TRAINING
# ============================================================================

class DigitRecognitionModel:
    """CNN-based handwritten digit recognition model"""
    
    def __init__(self):
        self.model = None
        self.history = None
        
    def build_cnn_model(self, input_shape=(8, 8, 1)):
        """Build CNN model for digit recognition"""
        self.model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=input_shape, padding='same'),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu', padding='same'),
            MaxPooling2D((2, 2)),
            Flatten(),
            Dense(128, activation='relu'),
            Dropout(0.5),
            Dense(10, activation='softmax')
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return self.model
    
    def train(self, X_train, y_train, X_test, y_test, epochs=50, batch_size=32):
        """Train the model"""
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            verbose=0
        )
        
        return self.history
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        test_loss, test_accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        return test_loss, test_accuracy
    
    def predict(self, X):
        """Make predictions"""
        predictions = self.model.predict(X, verbose=0)
        return np.argmax(predictions, axis=1)

# ============================================================================
# 5. MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print("HANDWRITTEN DIGIT RECOGNITION SYSTEM")
    print("Using Convolutional Neural Networks and Deep Learning")
    print("=" * 80)
    
    # Load dataset
    print("\n[Step 1] Loading Handwritten Digit Dataset...")
    X, y, digits = load_digit_dataset()
    
    # Preprocess data
    print("\n[Step 2] Preprocessing Data...")
    X_train, X_test, y_train, y_test = preprocess_data(X, y)
    
    # Generate visualizations
    print("\n[Step 3] Generating Visualizations...")
    print("Creating sample digits visualization...")
    visualize_sample_digits(digits)
    
    print("Creating digit distribution visualization...")
    visualize_digit_distribution(y)
    
    print("Creating pixel intensity visualization...")
    visualize_pixel_intensity(X, y)
    
    # Build and train model
    print("\n[Step 4] Building and Training CNN Model...")
    model = DigitRecognitionModel()
    model.build_cnn_model()
    
    print("Training model...")
    history = model.train(X_train, y_train, X_test, y_test, epochs=50, batch_size=32)
    
    # Evaluate model
    print("\n[Step 5] Evaluating Model Performance...")
    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    print(f"Test Loss: {test_loss:.4f}")
    print(f"Test Accuracy: {test_accuracy:.4f}")
    
    # Make predictions
    print("\nMaking predictions on test set...")
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    print(f"\nDetailed Performance Metrics:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    
    # Generate additional visualizations
    print("\n[Step 6] Generating Additional Visualizations...")
    print("Creating training history visualization...")
    visualize_training_history(history)
    
    print("Creating confusion matrix...")
    visualize_confusion_matrix(y_test, y_pred)
    
    print("Creating prediction examples...")
    visualize_prediction_examples(X_test, y_test, y_pred)
    
    # Model performance comparison
    results = {
        'CNN Model': {
            'Accuracy': accuracy,
            'Precision': precision,
            'Recall': recall,
            'F1-Score': f1
        }
    }
    
    print("Creating model performance comparison...")
    visualize_model_performance(results)
    
    # Print classification report
    print("\n" + "=" * 80)
    print("CLASSIFICATION REPORT")
    print("=" * 80)
    print(classification_report(y_test, y_pred, target_names=[str(i) for i in range(10)]))
    
    print("\n" + "=" * 80)
    print("EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nGenerated Visualizations:")
    print("  1. sample_digits.png")
    print("  2. digit_distribution.png")
    print("  3. pixel_intensity.png")
    print("  4. training_history.png")
    print("  5. confusion_matrix.png")
    print("  6. prediction_examples.png")
    print("  7. model_performance.png")
    
    return X, y, X_train, X_test, y_train, y_test, model, history, results

if __name__ == "__main__":
    X, y, X_train, X_test, y_train, y_test, model, history, results = main()
