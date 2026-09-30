"""
Image Preprocessing Utilities and Dataset Generation for Handwritten Digit Recognition
Provides utilities for image processing, feature extraction, and dataset management
"""

import numpy as np
import pandas as pd
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
import cv2

class ImagePreprocessor:
    """
    Comprehensive image preprocessing utilities for digit recognition
    """
    
    def __init__(self):
        """Initialize the image preprocessor"""
        self.scaler = StandardScaler()
        
    def normalize_image(self, image):
        """Normalize image pixel values to 0-1 range"""
        return image / 16.0
    
    def standardize_image(self, image):
        """Standardize image using z-score normalization"""
        return (image - image.mean()) / (image.std() + 1e-8)
    
    def apply_gaussian_blur(self, image, kernel_size=3):
        """Apply Gaussian blur to smooth the image"""
        return cv2.GaussianBlur(image.astype(np.uint8), (kernel_size, kernel_size), 0)
    
    def apply_threshold(self, image, threshold_value=8):
        """Apply binary threshold to the image"""
        binary_image = np.where(image > threshold_value, 1, 0)
        return binary_image
    
    def extract_features(self, image):
        """
        Extract comprehensive features from digit image
        """
        features = {}
        
        # Basic statistics
        features['mean_intensity'] = np.mean(image)
        features['std_intensity'] = np.std(image)
        features['max_intensity'] = np.max(image)
        features['min_intensity'] = np.min(image)
        
        # Spatial features
        features['center_of_mass_x'] = np.sum(np.arange(image.shape[0])[:, np.newaxis] * image) / (np.sum(image) + 1e-8)
        features['center_of_mass_y'] = np.sum(np.arange(image.shape[1])[np.newaxis, :] * image) / (np.sum(image) + 1e-8)
        
        # Edge features
        edges = cv2.Canny(image.astype(np.uint8) * 255, 50, 150)
        features['edge_count'] = np.sum(edges > 0)
        
        # Contour features
        contours, _ = cv2.findContours(image.astype(np.uint8) * 255, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        features['contour_count'] = len(contours)
        
        # Density features
        features['pixel_density'] = np.sum(image > 0) / image.size
        
        # Moment features
        M = cv2.moments(image.astype(np.uint8) * 255)
        if M['m00'] != 0:
            features['hu_moment_1'] = M['m20'] / (M['m00'] ** 2 + 1e-8)
            features['hu_moment_2'] = M['m02'] / (M['m00'] ** 2 + 1e-8)
        else:
            features['hu_moment_1'] = 0
            features['hu_moment_2'] = 0
        
        return features
    
    def extract_histogram_features(self, image, bins=8):
        """Extract histogram-based features"""
        hist = np.histogram(image.flatten(), bins=bins)[0]
        hist_normalized = hist / np.sum(hist)
        return hist_normalized


class DigitDatasetGenerator:
    """
    Generate and manage digit datasets for training and evaluation
    """
    
    def __init__(self):
        """Initialize the dataset generator"""
        self.digits = load_digits()
        self.preprocessor = ImagePreprocessor()
        
    def get_dataset_info(self):
        """Get comprehensive dataset information"""
        info = {
            'total_samples': len(self.digits.data),
            'image_shape': (8, 8),
            'num_classes': 10,
            'num_features': self.digits.data.shape[1],
            'pixel_range': (self.digits.data.min(), self.digits.data.max())
        }
        return info
    
    def get_class_distribution(self):
        """Get the distribution of classes in the dataset"""
        unique, counts = np.unique(self.digits.target, return_counts=True)
        distribution = {}
        for digit, count in zip(unique, counts):
            distribution[digit] = {
                'count': count,
                'percentage': count / len(self.digits.target) * 100
            }
        return distribution
    
    def get_samples_by_digit(self, digit, num_samples=5):
        """Get sample images for a specific digit"""
        indices = np.where(self.digits.target == digit)[0]
        selected_indices = np.random.choice(indices, min(num_samples, len(indices)), replace=False)
        samples = self.digits.data[selected_indices]
        return samples.reshape(-1, 8, 8)
    
    def extract_dataset_features(self):
        """
        Extract comprehensive features for all samples in the dataset
        """
        feature_list = []
        
        for idx, image_flat in enumerate(self.digits.data):
            image = image_flat.reshape(8, 8)
            features = self.preprocessor.extract_features(image)
            features['digit'] = self.digits.target[idx]
            features['sample_id'] = idx
            feature_list.append(features)
        
        return pd.DataFrame(feature_list)
    
    def get_statistics_by_digit(self):
        """Get statistical information for each digit class"""
        stats = {}
        
        for digit in range(10):
            digit_data = self.digits.data[self.digits.target == digit]
            stats[digit] = {
                'count': len(digit_data),
                'mean_intensity': digit_data.mean(),
                'std_intensity': digit_data.std(),
                'min_intensity': digit_data.min(),
                'max_intensity': digit_data.max()
            }
        
        return stats


def generate_and_save_datasets(output_dir='/home/ubuntu'):
    """
    Generate and save all sample datasets
    """
    print("Generating handwritten digit datasets...")
    
    # Initialize generator
    generator = DigitDatasetGenerator()
    
    # Get dataset information
    print("  Extracting dataset information...")
    info = generator.get_dataset_info()
    print(f"    Total Samples: {info['total_samples']}")
    print(f"    Image Shape: {info['image_shape']}")
    print(f"    Number of Classes: {info['num_classes']}")
    
    # Get class distribution
    print("  Analyzing class distribution...")
    distribution = generator.get_class_distribution()
    for digit, data in distribution.items():
        print(f"    Digit {digit}: {data['count']} samples ({data['percentage']:.1f}%)")
    
    # Extract features
    print("  Extracting comprehensive features...")
    features_df = generator.extract_dataset_features()
    features_path = f'{output_dir}/digit_features.csv'
    features_df.to_csv(features_path, index=False)
    print(f"  ✓ Features saved to {features_path}")
    
    # Get statistics
    print("  Calculating digit statistics...")
    stats = generator.get_statistics_by_digit()
    
    stats_list = []
    for digit, stat_data in stats.items():
        stats_list.append({
            'Digit': digit,
            'Sample_Count': stat_data['count'],
            'Mean_Intensity': stat_data['mean_intensity'],
            'Std_Intensity': stat_data['std_intensity'],
            'Min_Intensity': stat_data['min_intensity'],
            'Max_Intensity': stat_data['max_intensity']
        })
    
    stats_df = pd.DataFrame(stats_list)
    stats_path = f'{output_dir}/digit_statistics.csv'
    stats_df.to_csv(stats_path, index=False)
    print(f"  ✓ Statistics saved to {stats_path}")
    
    # Save raw dataset
    print("  Saving raw dataset...")
    raw_data = generator.digits.data
    raw_labels = generator.digits.target
    
    raw_df = pd.DataFrame(raw_data)
    raw_df['digit'] = raw_labels
    raw_path = f'{output_dir}/digit_dataset_raw.csv'
    raw_df.to_csv(raw_path, index=False)
    print(f"  ✓ Raw dataset saved to {raw_path}")
    
    return features_df, stats_df, raw_df


if __name__ == '__main__':
    features_df, stats_df, raw_df = generate_and_save_datasets()
    
    print("\nDataset Summary:")
    print(f"Total Features Extracted: {len(features_df)}")
    print(f"Feature Columns: {list(features_df.columns)}")
    
    print("\nFeature Statistics:")
    print(features_df.describe())
    
    print("\nDigit Statistics:")
    print(stats_df)
