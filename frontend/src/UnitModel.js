import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader.js';

const UnitModel = ({ modelPath, width = 400, height = 400 }) => {
  const mountRef = useRef();

  useEffect(() => {
    // Set up the scene, camera, and renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xeeeeee);

    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(0, 2, 5);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    mountRef.current.appendChild(renderer.domElement);

    // Add some basic lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 7.5);
    scene.add(directionalLight);

    // Load the base model FBX
    const loader = new FBXLoader();
    loader.load(
      modelPath,
      (object) => {
        // Optionally adjust scale or position if needed:
        object.scale.set(0.01, 0.01, 0.01);
        scene.add(object);
      },
      (xhr) => {
        // onProgress callback (optional)
        console.log((xhr.loaded / xhr.total) * 100 + '% loaded');
      },
      (error) => {
        console.error('An error happened while loading the model:', error);
      }
    );

    // Animation loop (for rendering, even if nothing animates)
    const animate = () => {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    // Clean up on unmount
    return () => {
      mountRef.current.removeChild(renderer.domElement);
      renderer.dispose();
    };
  }, [modelPath, width, height]);

  return <div ref={mountRef} style={{ width, height }} />;
};

export default UnitModel;
